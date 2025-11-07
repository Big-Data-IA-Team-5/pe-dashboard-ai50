"""LLM client wrapper for PE dashboard generation."""
import os
import time
from pathlib import Path
from typing import Optional
from openai import OpenAI, RateLimitError, APIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMClient:
    """Wrapper for OpenAI API calls with retry logic and error handling."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize LLM client.
        
        Args:
            model: OpenAI model to use (gpt-4o-mini is faster and cheaper)
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Make sure .env file exists and is loaded."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # Load concise system prompt - prefer PE_Dashboard_Concise.md
        prompt_path = Path(__file__).parent.parent / "PE_Dashboard_Concise.md"
        if not prompt_path.exists():
            # Fallback to original
            prompt_path = Path(__file__).parent.parent / "PE_Dashboard.md"
            print(f"⚠️  Using PE_Dashboard.md (concise version not found)")
        
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"System prompt not found. Need PE_Dashboard_Concise.md or PE_Dashboard.md"
            )
        
        self.system_prompt = prompt_path.read_text()
        print(f"✓ System prompt loaded from: {prompt_path.name} ({len(self.system_prompt)} chars)")
        print(f"✓ LLM Client initialized")
        print(f"  Model: {self.model}")
        print(f"  Prompt loaded: {len(self.system_prompt)} chars")
    
    def generate_dashboard(
        self,
        context: str,
        max_tokens: int = 4000,
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> str:
        """
        Generate PE dashboard from context.
        
        Args:
            context: Either JSON payload (structured) or retrieved text (RAG)
            max_tokens: Maximum tokens in response (4000 ≈ 3000 words)
            temperature: 0.0-1.0, lower = more deterministic
            max_retries: Number of retry attempts on rate limit
            
        Returns:
            Markdown dashboard string with 8 required sections
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self.system_prompt
                        },
                        {
                            "role": "user",
                            "content": f"Generate complete PE dashboard:\n\n{context}"
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return response.choices[0].message.content
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                    print(f"⚠️  Rate limit hit, waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    error_msg = (
                        "## Error\n\n"
                        f"OpenAI rate limit exceeded after {max_retries} retries.\n"
                        "Please wait a moment and try again."
                    )
                    return error_msg
                    
            except APIError as e:
                error_msg = (
                    "## Error\n\n"
                    f"OpenAI API error: {str(e)}\n"
                    "Please check your API key and try again."
                )
                return error_msg
            
            except Exception as e:
                error_msg = (
                    "## Error\n\n"
                    f"Unexpected error generating dashboard: {str(e)}"
                )
                return error_msg
        
        return "## Error\n\nMaximum retries exceeded."
    
    def validate_structure(self, markdown: str) -> dict:
        """
        Validate that dashboard has all 8 required sections.
        
        Args:
            markdown: Generated dashboard markdown
            
        Returns:
            {
                "valid": bool,
                "missing_sections": list,
                "present_sections": list,
                "has_disclosure_gaps": bool,
                "section_count": int
            }
        """
        required_sections = [
            "## Company Overview",
            "## Business Model and GTM",
            "## Funding & Investor Profile",
            "## Growth Momentum",
            "## Visibility & Market Sentiment",
            "## Risks and Challenges",
            "## Outlook",
            "## Disclosure Gaps"
        ]
        
        present = [s for s in required_sections if s in markdown]
        missing = [s for s in required_sections if s not in markdown]
        
        return {
            "valid": len(missing) == 0,
            "missing_sections": missing,
            "present_sections": present,
            "has_disclosure_gaps": "## Disclosure Gaps" in markdown,
            "section_count": len(present)
        }
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 4000) -> float:
        """
        Estimate cost for a generation.
        
        Args:
            input_tokens: Approximate input tokens
            output_tokens: Approximate output tokens
            
        Returns:
            Estimated cost in USD
        """
        # gpt-4o-mini pricing (as of Nov 2024)
        input_cost_per_1k = 0.000150  # $0.15 per 1M tokens
        output_cost_per_1k = 0.000600  # $0.60 per 1M tokens
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create LLM client singleton.
    
    Returns:
        Initialized LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


# Test function
def test_llm_client():
    """Test LLM client with simple prompt."""
    from dotenv import load_dotenv
    load_dotenv()
    
    client = get_llm_client()
    
    test_context = """
    Company: TestAI Inc.
    Founded: 2023
    Headquarters: San Francisco, CA
    Funding: $10M Series A from Sequoia Capital
    Products: Enterprise AI automation platform
    
    Generate a PE dashboard for this company.
    """
    
    print("Testing dashboard generation...")
    dashboard = client.generate_dashboard(test_context)
    
    print("\n" + "="*60)
    print(dashboard)
    print("="*60)
    
    validation = client.validate_structure(dashboard)
    print(f"\n✅ Validation: {validation['section_count']}/8 sections")
    
    if not validation['valid']:
        print(f"⚠️  Missing: {validation['missing_sections']}")
    else:
        print("✓ All required sections present")
    
    return dashboard


if __name__ == "__main__":
    test_llm_client()
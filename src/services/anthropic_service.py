import re

import anthropic

from app_config import get_settings
from schemas.rerank_result import RerankResult


class AnthropicService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnthropicService, cls).__new__(cls)
            cls._instance.client = anthropic.AsyncAnthropic(api_key=get_settings().ANTHROPIC_API_KEY)
        return cls._instance

    async def isolate_article_text(self, article_text: str) -> str:
        """
        Use a cheaper model to get rid of unnecessary information
        :param article_text:
        :return:
        """
        prompt = f"""
        Here is the raw text input:

        <raw_text>
        {article_text}
        </raw_text>
        
        Your task is to extract only the main article content from this raw text, removing all extraneous information. Follow these guidelines:
        
        1. Identify and remove the following types of unnecessary information:
           - Cookie information and consent notices
           - Advertising content
           - Tracker information
           - Embedded social media handles
           - Privacy policies
           - Terms and conditions
           - Site information
           - Navigation menus
           - Footer content
           - Author biographies (unless they are integral to the article)
           - Related article links
           - Comments sections
        
        2. Maintain the original wording, spelling, and formatting of the article content. Do not paraphrase or summarize.
        
        3. If there are multiple articles or unrelated content blocks, focus on extracting the main article only.
        
        4. In cases where it's unclear whether certain text belongs to the article or is extraneous, err on the side of inclusion to avoid losing potentially important content.
        
        Once you have extracted the article content, present it in the following format:
        
        <extracted_article>
        [Insert the extracted article content here, preserving original formatting]
        </extracted_article>
        """
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            system="You are tasked with extracting the main article content from a raw text input that contains both the article and extraneous information. Your goal is to remove all unnecessary elements while preserving the original article text.",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            stop_sequences=["</extracted_article>"],
        )

        # Define a regex pattern to extract content between the <extracted_article> tags
        pattern = r"<extracted_article>(.*?)</extracted_article>"
        matches = re.search(pattern, response.content[0].text, re.DOTALL)
        if matches:
            return matches.group(1)

        return response.content[0].text

    async def summarise_crypto_news_artice(self, article_text: str) -> str:
        """
        Given the input artice, summarise and return the summary
        """
        prompt = f"""
        Summarise the following news article. 
        
        <raw_text>
        {article_text}
        </raw_text>
        
        Focus on these key aspects:

        Nature of the News (positive, negative, or neutral tones)
        Assess the overall sentiment (Quantify the sentiment score from 1 - 5 (low - high respectively) if possible.), Give this in the format "Sentiment Score: score"
        Regulatory Changes: Laws, regulations, or government actions affecting cryptocurrencies (if mentioned)
        Technological Updates: Protocol upgrades, hard forks, or new feature releases (if mentioned)
        Security Incidents: Hacks, scams, or vulnerabilities discovered (if mentioned)
        Market Milestones: All-time highs/lows, significant trading volumes, or market cap changes (if mentioned)
        Adoption and Partnerships: Collaborations with companies, institutions, or acceptance as payment (if mentioned)
        Macroeconomic Factors: Inflation rates, interest rates, or economic policies that impact crypto markets (if mentioned)
        Quotes and Statements: Comments from industry leaders, CEOs, government officials, or influential investors (if mentioned)
        Historical Context: Previous events that relate to the current news (if mentioned)
        Financial Figures: Investment amounts, market capitalization changes, or transaction volumes (if mentioned)
        Statistical Trends: Data on trading volumes, price changes, or volatility indexes (if mentioned)
        Short-term vs. Long-term Effects: Immediate market reactions versus potential future implications (if mentioned)
        Technical Analysis Indicators (if mentioned)
        
        Once you have summarised the article content, present it in the following format:
        
        <summarised_article>
        [Insert the summarised article content here]
        </summarised_article>
        """

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": "You are a financial analyst specializing in using cryptocurrency news to predict price movements. Your task is to analyze and summarize a news article, focusing on key aspects that could impact cryptocurrency markets.",
                },
            ],
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt},
            ],
            stop_sequences=["</summarised_article>"],
        )

        # Define a regex pattern to extract content between the <summarised_article> tags
        pattern = r"<summarised_article>\s*(.*?)\s*</summarised_article>"
        matches = re.search(pattern, response.content[0].text, re.DOTALL)
        if matches:
            return matches.group(1)

        return response.content[0].text

    async def answer_question(self, question: str, results: list[RerankResult]) -> str:
        context = "\n\n".join(f"<article>\n{r.content}\n</article>" for r in results)

        prompt = f"""
        Use the the below article list of financial context to answer the question. Each article in the list starts with 
        '<article>' and ends with '</article>'. This is important as the sentiment score of each article indicates the significance the article's content should
        contribute to your answer. Here is the context:

        <context>
        {context}
        </context>
        
        Now, I will present you with a question. Your goal is to answer it accurately and concisely using only the information provided in the context above.
        
        <question>
        {question}
        </question>
        
        Instructions for answering:
        
        1. Carefully read and analyze the provided context and question.
        2. Formulate your answer using only the information given in the context. Do not introduce any external information or make assumptions beyond what is explicitly stated.
        3. Provide a clear and concise answer. Avoid unnecessary elaboration or speculation.
        4. If the question asks for a prediction, base your prediction solely on the trends and data provided in the context. Clearly state that it is a prediction based on the given information.
        5. If you cannot answer the question based on the provided context, state that the information is not available in the given context.
        
        Output your answer in the following format:
        
        <answer>
        Your concise and clear answer here, based solely on the provided context.
        </answer>
        
        Remember, accuracy and clarity are key. Do not hallucinate or include information not present in the given context.
        """

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": "You are a financial analyst AI assistant. Your task is to answer questions based solely on the provided financial context. Do not use any external knowledge or make assumptions beyond what is explicitly stated in the context.",
                },
            ],
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt},
            ],
            stop_sequences=["</answer>"],
        )

        pattern = r"<answer>\s*(.*?)\s*</answer>"
        matches = re.search(pattern, response.content[0].text, re.DOTALL)
        if matches:
            return matches.group(1)

        return response.content[0].text

    async def predict(self, results: list[RerankResult]) -> str:
        context = "\n\n".join(f"<article>\n{r.content}\n</article>" for r in results)

        prompt = f"""
        Use the the below article list of financial context to answer this question. Each article in the list starts with 
        '<article>' and ends with '</article>'. This is important as the sentiment score of each article indicates the significance the article's content should
        contribute to your answer. Here is the context:

        <context>
        {context}
        </context>

        Now, I will present you with a list of instructions. Your goal is to answer it accurately and concisely using only the information provided in the context above.

       <instructions>
        Please analyze these news articles and provide:
        1. Overall market sentiment analysis
        2. Key trends and patterns across articles
        3. Potential market impact assessment
        4. Price movement prediction with confidence level
        5. Risk factors and uncertainties
        6. Technical and fundamental analysis correlation
        7. Timeline of potential market reactions
        8. Conflicting narratives or contradictions
        9. Volume and liquidity implications
        10. Geographic and regulatory considerations
        
        For the prediction, consider:
        - Short-term (24h) outlook
        - Medium-term (7d) outlook
        - Long-term (30d) outlook
        
        Include confidence levels (Low/Medium/High) for each prediction.  Remember, accuracy and clarity are key. Do not hallucinate or include information not present in the given context.
        </instructions>

        <answer>
        Your concise and clear answer here, based solely on the provided context.
        </answer>
        """

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": "You are a financial analyst AI assistant. Your task is to answer questions based solely on the provided financial context. Do not use any external knowledge or make assumptions beyond what is explicitly stated in the context.",
                },
            ],
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt},
            ],
            stop_sequences=["</answer>"],
        )

        pattern = r"<answer>\s*(.*?)\s*</answer>"
        matches = re.search(pattern, response.content[0].text, re.DOTALL)
        if matches:
            return matches.group(1)

        return response.content[0].text

    def get_sentiment_score(self, summary: str) -> int:
        """
        A summary always has a sentiment score embedded in the text as such 'Sentiment Score: <score>'
        """
        # Define a regex pattern to capture the sentiment score
        pattern = r"Sentiment Score:\s*(\d+)"
        match = re.search(pattern, summary)

        if match:
            return int(match.group(1))
        return 0

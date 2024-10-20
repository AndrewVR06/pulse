import asyncio

from services.summary_service import SummaryService
from services.vector_service import VectorService

s = VectorService()
ss = SummaryService()

text = """
The Best Crypto Casino & Crypto Betting - Claim 5 BTC Daily Free Bonus! The World's Fastest Growing Crypto casino and Sports Book. - Claim 200% Deposit Bonus & 50 Free Spins with no Wagering!                   Some of the biggest price predictions forecasted $5.58 for APE in a few years. TL:DR; CryptoPotato   reported  earlier today the massive achievement by ApeCoin’s team. After months of standing on the sidelines without attracting significant attention from the general public, the devs announced the official launch of the ApeChain bridge. It allows investors to earn native yield on assets such as APE, ETH, and a few stablecoins. Automatic Yield Mode ON APECHAIN: This is the default mode for all externally owned accounts (EOAs), where yield is automatically earned each block. The address’s APE balance is incremented by the amount of yield earned each block without the need for manual intervention. — ApeCoin (@apecoin)  October 20, 2024 The effects on APE’s price were immediate as the asset skyrocketed by over 65% at one point and neared $1.3 for the first time since June. It became the top performer over the otherwise dull weekend and  returned  to the largest 100 altcoins by market cap, with its own shooting up to $900 million earlier today. As such, we asked Perplexity, the popular AI chatbot, about APE’s potential to grow further in the upcoming months and years, given the developments around the underlying project. The ChatGPT rival outlined a target of $1.36 for APE during October, which means that the asset might have already peaked this month. It also foresees a minor retracement and calmer price fluctuations in November. However, Perplexity is bullish on APE for the next few years. It said the asset could surge to $1.92 next year, $2.2 in 2026, and up to $5.58 by 2030. Nevertheless, these levels are still far from APE’s all-time high, registered in April 2022 of $26.7. Perplexity believes there are three main factors that could influence a potential price surge for APE: 
											Jordan got into crypto in 2016 by trading and investing. He began writing about blockchain technology in 2017 and now serves as CryptoPotato's Assistant Editor-in-Chief. He has managed numerous crypto-related projects and is passionate about all things blockchain.  Contact Jordan:  LinkedIn 
										   Sign-up FREE to receive our extended daily market update and coin analysis report
"""
asyncio.run(ss.isolate_article_text(text))

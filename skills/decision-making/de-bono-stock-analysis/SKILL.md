---
name: de-bono-stock-analysis
description: Use De Bono's Six Thinking Hats framework to analyze stock market moves based on geopolitical events
tags: [decision-making, stock-analysis, geopolitics, de-bono]
version: 1.0.0
---

# De Bono Stock Analysis Framework

Use this skill to apply De Bono's Six Thinking Hats to stock market analysis, particularly for geopolitical events affecting specific stocks.

## When to Use

- Analyzing how geopolitical events (wars, sanctions, trade deals) will impact specific stocks
- Making buy/sell/hold decisions based on complex multi-factor analysis
- When Dwayne asks about his Shell (SHEL) stock holdings (he holds 100 shares)
- Any stock market decision requiring structured, multi-perspective analysis

## The Six Hats Framework

1. **WHITE HAT (Facts)**
   - Current stock price, trading volume, analyst ratings
   - Company fundamentals (earnings, revenue, debt)
   - Geopolitical facts (sanctions, blockades, trade flows)
   - Historical precedent data (similar past events)
   - Quantitative data only — no opinions

2. **RED HAT (Gut/Emotions)**
   - Market sentiment, fear/greed indicators
   - Investor psychology around the event
   - Emotional pendulum swings (buy the rumor/sell the news)
   - Gut feelings about market overreaction/underreaction

3. **BLACK HAT (Risks/Caution)**
   - Downside scenarios, worst-case outcomes
   - Hidden risks, regulatory threats
   - Competitor advantages, market share erosion
   - Macroeconomic headwinds, recession risks
   - Why this could go very wrong

4. **YELLOW HAT (Optimism/Upsides)**
   - Best-case scenarios, upside potential
   - Competitive advantages, market opportunities
   - Strategic positioning benefits
   - Why this could go very right
   - Long-term growth prospects

5. **GREEN HAT (Creativity/Alternatives)**
   - Wild card scenarios, black swan events
   - Alternative investment strategies
   - Creative hedging approaches
   - Unconventional market dynamics
   - "What if" thinking

6. **BLUE HAT (Process/Control)**
   - Synthesizes all other hats' perspectives
   - Creates clear recommendation with confidence level
   - Suggests specific actions (buy/sell/hold/hedge)
   - Identifies key monitoring indicators
   - Provides timeline for re-evaluation

## Execution Pattern

1. **Identify the trigger event** (e.g., "Iran blockade ends with US deal")
2. **Identify the affected stock** (e.g., "Shell/SHEL")
3. **Run all 6 hats concurrently** using delegate_tool with max_concurrent_children: 6
4. **Synthesize outputs** into clear recommendation
5. **Provide specific action guidance** for Dwayne's holdings

## Example: Shell Stock Analysis

**Trigger:** "If the blockade ends and they have a deal, what will happen to my Shell stock?"

**White Hat Facts:**
- Shell at $91.36, up ~15% over past month due to oil surge
- Brent crude at $102-104/barrel with $20-30 risk premium
- 2015 Iran deal precedent: oil dropped 2-6%, energy stocks fell
- Shell's earnings sensitivity: each $10/barrel change impacts annual earnings by $2-3B

**Red Hat Gut:**
- Stock will take a serious hit — current surge built on geopolitical tension
- Emotional pendulum swings from "buy the chaos" to "sell the resolution"

**Black Hat Risks:**
- Iranian oil flood (1-1.5M barrels/day) could drive prices to $58-70 range
- Shell's trading division profits from volatility — that revenue stream evaporates

**Yellow Hat Upsides:**
- Strait reopening restores Qatari Pearl production (920-980K boed vs current 880-920K)
- Unlocks billions in trapped working capital ($10-15B swing)

**Green Hat Wild Ideas:**
- Shell becomes hybrid security — part energy stock, part geopolitical instrument
- Stock price inversely correlated with traditional energy markets

**Blue Hat Synthesis:**
- Medium confidence that Shell stock drops 5-15% short-term
- Could recover within 6-12 months as operational benefits materialize
- **Action:** If risk-averse, consider trimming before deal announcement. If long-term bullish, hold through volatility.

## Configuration Note

For concurrent execution of all 6 hats, ensure delegation.max_concurrent_children is set to 6 in Hermes config. Dwayne has already patched this in his config.yaml.

## Pitfalls to Avoid

- Don't run more than 6 concurrent sub-agents (system limit)
- Ensure each hat stays in-character (no cross-hat contamination)
- Always include specific action recommendations for Dwayne's holdings
- Remember Dwayne holds 100 shares of Shell (SHEL)
- Balance quantitative data with qualitative market psychology

## Verification

After running analysis:
1. Check that all 6 perspectives were covered
2. Verify synthesis includes confidence level (low/medium/high)
3. Ensure specific action guidance is provided
4. Include timeline for re-evaluation if appropriate
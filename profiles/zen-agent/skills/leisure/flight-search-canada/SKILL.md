---
name: flight-search-canada
description: Search for cheap flights to Canada from US cities, with comprehensive research methodology and booking strategies.
---

Use this skill when a user wants to find cheap flights to Canada, especially for next-week travel.

## Goal
Find the best flight options to Canada based on user's departure city, destination, dates, and budget constraints.

## Workflow

1. **Gather essential details** (ask if not provided):
   - Departure city (and preferred airport)
   - Destination city in Canada
   - Travel dates (departure and return if round-trip)
   - Number of passengers
   - Budget constraints
   - Preferred airlines or cabin class
   - Flexibility on dates/times

2. **Initial research phase:**
   - Search for general flight deals to Canada using web_search
   - Check Air Canada's promotional pages for specific routes
   - Look at Alaska Airlines for West Coast departures
   - Search Cheapflights, Kayak, and Momondo for comparison

3. **Extract detailed pricing:**
   - Use web_extract on airline promotional pages
   - Focus on dates close to user's travel window
   - Note baggage fees and restrictions
   - Check for nearby airport alternatives

4. **Analyze and compare options:**
   - Create comparison table of top 3-5 options
   - Include total price, travel time, layovers, airline quality
   - Note any special restrictions (Basic Economy vs Regular)
   - Consider value factors: schedule convenience, baggage allowance, change policies

5. **Provide recommendations:**
   - Best value option (price + convenience)
   - Cheapest option (absolute lowest price)
   - Most convenient option (direct flights, best times)
   - Booking tips specific to the route

6. **Next steps guidance:**
   - How to book (direct vs OTA)
   - When to book for best price
   - What to watch out for (hidden fees, restrictions)
   - Alternative options if primary choices are sold out

## Key Resources

### Airlines with Best Canada Deals:
1. **Air Canada** - National carrier, most routes, often has promotional fares
2. **Alaska Airlines** - Best for West Coast to Western Canada
3. **Porter Airlines** - Excellent for Eastern Canada, high customer ratings
4. **United Airlines** - Good connectivity through Star Alliance
5. **Delta** - Competitive on major routes

### Useful Websites:
- Air Canada promotional pages: `https://www.aircanada.com/en-us/flights-from-[CITY]-to-canada`
- Alaska Airlines Canada flights: `https://www.alaskaair.com/en/flights-to-canada`
- Cheapflights Canada page: `https://www.cheapflights.com/flights-to-canada/`
- Kayak Air Canada deals: `https://www.kayak.com/flight-routes/Air-Canada-United-States-US0/Canada-CA0`

### Popular Canadian Destinations:
1. **Toronto (YYZ/YTZ)** - Most popular, best connectivity
2. **Vancouver (YVR)** - West coast gateway, scenic
3. **Montréal (YUL)** - Cultural hub, French influence
4. **Calgary (YYC)** - Gateway to Canadian Rockies
5. **Ottawa (YOW)** - Capital city
6. **Halifax (YHZ)** - East coast maritime

## Pricing Benchmarks (as of April 2026)
- **Seattle to Vancouver**: From $79 (Air Canada)
- **New York to Toronto**: From ~$105 USD (Air Canada)
- **Los Angeles to Vancouver**: From $205 (Alaska Airlines)
- **Chicago to Toronto**: From ~$100 USD (Air Canada)
- **Boston to Canada**: From $91 (various)

## Booking Strategies

1. **Timing:**
   - Book on Thursdays for best prices
   - Search 1-2 weeks in advance for optimal pricing
   - Be flexible with dates (mid-week cheaper than weekends)

2. **Airport alternatives:**
   - Toronto: Consider YTZ (Billy Bishop) vs YYZ (Pearson)
   - Vancouver: YVR is main, but consider nearby if flexible
   - Montréal: YUL (Trudeau) is main international

3. **Fare types:**
   - Basic Economy: Cheapest but most restrictive
   - Regular Economy: Better flexibility for slightly more
   - Always check baggage fees before comparing prices

4. **Currency considerations:**
   - Canadian prices in CAD, US prices in USD
   - Conversion rate affects value (check current rate)
   - Some US sites show CAD prices converted

## Common Pitfalls

1. **Dynamic pricing:** Fares change frequently, always verify current prices
2. **Hidden fees:** Budget airlines have strict baggage policies
3. **Airport confusion:** Canada has multiple airports in major cities
4. **Seasonal variations:** Summer and holidays are more expensive
5. **Last-minute deals:** Rare for Canada routes, better to book in advance

## Verification Checklist

Before finalizing recommendations:
- [ ] All prices verified from current sources
- [ ] Baggage fees accounted for in total cost
- [ ] Travel dates match user's availability
- [ ] Airport codes correctly identified
- [ ] Alternative options presented
- [ ] Booking instructions clear and actionable
# Benchmark Prompts

This document contains 40 natural-language prompts across 8 functional groups designed to benchmark the BI Report Automation "Brain" against Julius AI. These prompts test the system's ability to interpret vague, complex, and potentially misleading intent and correctly translate it into a strictly-validated deterministic JSON Plan.

## 1. KPI Cards & Simple Aggregations
1. "Show me the total revenue, total number of orders, and average order value."
2. "Create a KPI for total customers."
3. "Give me the total distinct number of products sold."
4. "Show the total number of tickets." *(Edge case test: "tickets" should map to `count_rows`, not sum)*
5. "What is our overall profit margin percentage?"

## 2. Aggregations & Data Tables
6. "Give me a table of the top 10 countries by total sales."
7. "Show a pivot table of region vs product category with revenue as the values."
8. "I need a detailed table showing all customer names, their latest purchase date, and total spend."
9. "Provide a summary table grouping sales by both State and City."
10. "Build a table ranking our sales reps by quantity sold in descending order."

## 3. Trends & Time Series (with grain)
11. "Show the monthly sales trend over the last year."
12. "Plot the daily number of support tickets."
13. "Create a trend chart of quarterly profit."
14. "Show me year-over-year revenue growth by month."
15. "I want a line chart showing weekly active users over time."

## 4. Comparisons & Breakdowns
16. "Compare revenue between online and in-store channels."
17. "Show me a breakdown of sales by product category as a pie chart."
18. "I need a grouped bar chart comparing Q1 and Q2 sales across all regions."
19. "Show the market share of different brands using a donut chart."
20. "Compare the average age of customers by subscription tier."

## 5. Distributions & Outliers
21. "Show me the distribution of customer ages."
22. "I want a histogram of transaction amounts."
23. "Show me a box plot of salary by department."
24. "What does the spread of delivery times look like?"
25. "Plot a scatter chart of discount applied vs total order value."

## 6. Top-N & Filters / Time Ranges
26. "Show me the top 5 most profitable products."
27. "Show sales by region, but only for the year 2023."
28. "Give me a KPI for total sales, excluding the 'Cancelled' status."
29. "Show the bottom 10 performing stores by revenue."
30. "Show monthly trends for only our 'Enterprise' tier customers between Jan 1 and June 30."

## 7. Unusual/Complex Charts
31. "Show a waterfall chart of profit buildup by month."
32. "Create a funnel chart showing the conversion from Lead to Opportunity to Won."
33. "Show a treemap of revenue by product category and subcategory."
34. "Plot a combination chart: line for profit margin and bars for total revenue over time."
35. "Give me a decomposition tree for our operating costs."

## 8. Impossible / Misleading Requests (Graceful Failure)
36. "Plot Zip Code vs Month on a line chart." *(Should fail: Zip code is a code_geo, not a measure)*
37. "Sum the Customer IDs by Date." *(Should fail: Customer ID is an identifier, sum is invalid)*
38. "Show me a pie chart of daily sales for the last 5 years." *(Should fail/adapt: too many points for a pie chart)*
39. "Compare latitude and longitude on a bar chart." *(Should fail: meaningless visualization)*
40. "Give me the average phone number by region." *(Should fail: phone number is a string/identifier)*

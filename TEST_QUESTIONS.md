# CRM Data Agent Test Questions

## Instructions
Use these questions to test the capabilities of your CRM Data Agent. Start with the easier questions and progress to more complex ones to validate different aspects of the system.

## Test Questions

### 1. Basic Data Analysis (Easy)
**Question**: "What are the top 5 customers by total opportunity value?"

**Expected capabilities tested**:
- Basic SQL generation
- Simple aggregation and sorting
- Data visualization (bar chart or table)
- Business context understanding

---

### 2. Lead Source Analysis (Medium)
**Question**: "Which lead sources are performing best in terms of conversion rate and total value generated?"

**Expected capabilities tested**:
- Multi-table joins (Lead, Opportunity tables)
- Conversion rate calculations
- Comparative analysis
- Business metrics understanding
- Chart generation for comparison

---

### 3. Time-based Trend Analysis (Medium-Hard)
**Question**: "Show me the monthly sales trend for the last 12 months and identify any seasonal patterns."

**Expected capabilities tested**:
- Date/time handling and filtering
- Temporal data aggregation
- Trend analysis
- Time series visualization
- Pattern recognition insights

---

### 4. Complex Business Intelligence (Hard)
**Question**: "What is the average deal size and sales cycle length by region, and which regions have the highest customer lifetime value?"

**Expected capabilities tested**:
- Multi-dimensional analysis
- Complex calculations (averages, cycle lengths)
- Geographic data handling
- Customer lifetime value computation
- Multi-metric visualization
- Regional comparison insights

## Expected Outputs
For each question, the agent should provide:
- ✅ **SQL Query**: Generated and executed successfully
- ✅ **Data Results**: Accurate data retrieval
- ✅ **Visualization**: Interactive Vega-Lite charts
- ✅ **Business Insights**: Actionable recommendations
- ✅ **Context**: Explanation of findings and implications

## Testing Notes
- Test one question at a time
- Observe the multi-agent workflow (BA → DE → BI → Analysis)
- Check for accurate SQL generation and execution
- Verify chart interactivity and visual appeal
- Evaluate business insight quality and relevance
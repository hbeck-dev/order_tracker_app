# Memory - Order Tracker Project & Collaboration Notes

## Project Summary
**Order Tracker Streamlit App** - A web-based interface for tracking restaurant orders with CRUD functionality. Converts CLI-based order tracking system to interactive web app using Streamlit.

### Tech Stack
- **Framework**: Streamlit
- **Data Storage**: Text files (order_history.txt, prices.txt)
- **Language**: Python 3
- **Location**: `C:\Users\hc52y\OneDrive\Desktop\python\`

## File Structure

### Data Files
- **order_history.txt** (append-only log)
  - Format: `TIMESTAMP: NAME | LOCATION | ORDER | $PRICE`
  - Example: `2026-04-27 12:05:30: John | Chipotle | BURRITO, RICE, COKE | $12.50`
  - Used as source of truth for View Orders page

- **prices.txt** (updatable)
  - Format: `LOCATION | ORDER | $PRICE`
  - Example: `Chipotle | BURRITO, RICE, COKE | $12.50`
  - Used for Update Prices page
  - Can be edited without timestamp/name

### Code Files
- **order_tracker_new.py** - Original CLI version (reference)
- **streamlit_app.py** - Current web app (KEEP UPDATED)

## App Architecture

### Pages
1. **Add Order** - Create new orders (saves to both files with timestamp)
2. **View Orders** - Read all orders with delete capability (sorted by Location)
3. **Update Prices** - Edit prices in prices.txt only

### Key Functions
- `read_order_history()` - Parses order_history.txt (includes timestamps/names)
- `read_prices_file()` - Parses prices.txt (location/order/price only)
- `delete_orders_by_history_index()` - Deletes from BOTH files by matching records
- `save_new_order()` - Writes to both files with proper formatting
- `update_price()` - Updates prices.txt only

## Important Implementation Details

### Delete Logic
- Delete operations work on order_history.txt indices
- Must match and remove corresponding entries in prices.txt
- Sorting indices in reverse prevents index-shifting bugs
- No confirmation dialog - instant deletion with checkbox pre-selection

### Session State
- Checkboxes in View Orders use `st.session_state.selected_orders` dictionary
- Critical for maintaining selection across re-renders
- Reset after deletion with `st.rerun()`

### Data Parsing Edge Cases
- Prices must be parsed as floats by removing "$" prefix
- Order strings may contain commas (e.g., "BURRITO, RICE, COKE")
- Timestamp format: `YYYY-MM-DD HH:MM:SS`
- Must handle empty strings for optional items (side/drink in Add Order)

## Design Decisions Made

1. **View Orders reads from order_history.txt** (not prices.txt)
   - Reason: order_history.txt has name and timestamp
   - Requires careful matching when deleting from prices.txt

2. **No traditional confirmation dialogs**
   - Reason: Streamlit doesn't support modal pop-ups well
   - Solution: Pre-selection via checkboxes + greyed-out button

3. **Two separate update/delete implementations**
   - Update Prices: Works on prices.txt indices directly
   - Delete: Works on order_history.txt indices, finds matches in prices.txt

## Known Limitations & Future Improvements

### Current Limitations
- Text file storage doesn't scale well (O(n) operations)
- No data validation (user can enter invalid prices)
- Cannot recover deleted data
- File corruption would lose all data

### Future Enhancements
- Migrate to SQLite database (would simplify delete/update logic)
- Add data validation and error handling
- Implement backup/undo functionality
- Add filtering/search capabilities
- Export to CSV

## Collaboration Notes for Next Session

### When Working Together Again:
1. **Ask about existing data** - Request sample data files to understand exact format
2. **Clarify data model upfront** - Ask which file is "source of truth" for each operation
3. **Provide test cases** - Create some test data to validate with
4. **Define edge cases** - Ask about duplicate orders, special characters, etc.

### About the Developer:
- **Style**: Direct communicator, provides clear requirements
- **Approach**: Student learning - prefers leading the direction while I implement
- **Feedback**: Iterative, willing to refine multiple times
- **Expectations**: Asks clarifying questions before implementing (good practice)

### Tips for Future Work:
- They value clean UI/UX (multiple iterations on design)
- They want explanations when confused (ask clarifying questions!)
- They're working on a final project (treat code quality accordingly)
- Streamlit-specific: They like visual feedback (success messages, statistics, balloons)

## Testing Checklist for Next Session

- [ ] Test adding new order with combo
- [ ] Test adding new order without combo (with all optional items)
- [ ] Test adding order with only required fields
- [ ] Test View Orders sorting by location
- [ ] Test checkboxes persist during scrolling
- [ ] Test delete single order
- [ ] Test delete multiple orders
- [ ] Test Update Prices from both pages
- [ ] Test with empty files
- [ ] Test file format preservation

## Command to Run App
```bash
cd "C:\Users\hc52y\OneDrive\Desktop\python"
streamlit run streamlit_app.py
```


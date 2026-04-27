"""
Order Tracker Streamlit Application

A web-based interface for tracking restaurant orders with CRUD functionality.
- Create: Add new orders
- Read: View all orders in a table format
- Update: Edit order prices
- Delete: Remove orders with confirmation
"""

import streamlit as st
import pandas as pd
import datetime
import os

# GLOBAL CONSTANTS
ORDERS_FILE = "order_history.txt"
PRICES_FILE = "prices.txt"

# Streamlit page configuration
st.set_page_config(page_title="Order Tracker", layout="wide", initial_sidebar_state="expanded")

# ==================== HELPER FUNCTIONS ====================

def read_prices_file():
    """Read prices.txt and return as a list of dictionaries."""
    if not os.path.exists(PRICES_FILE):
        return []
    
    orders = []
    try:
        with open(PRICES_FILE, "r") as file:
            for idx, line in enumerate(file):
                parts = line.strip().split("|")
                if len(parts) == 3:
                    orders.append({
                        "Index": idx,
                        "Location": parts[0].strip(),
                        "Order": parts[1].strip(),
                        "Price": parts[2].strip()
                    })
    except FileNotFoundError:
        pass
    return orders


def read_order_history():
    """Read order_history.txt and return as a list of dictionaries."""
    if not os.path.exists(ORDERS_FILE):
        return []
    
    orders = []
    try:
        with open(ORDERS_FILE, "r") as file:
            for idx, line in enumerate(file):
                if line.strip():
                    # Format: "TIMESTAMP: NAME | LOCATION | ORDER | $PRICE"
                    parts = line.strip().split(": ", 1)
                    if len(parts) == 2:
                        timestamp = parts[0]
                        rest = parts[1].split("|")
                        if len(rest) == 4:
                            orders.append({
                                "Index": idx,
                                "Timestamp": timestamp,
                                "Name": rest[0].strip(),
                                "Location": rest[1].strip(),
                                "Order": rest[2].strip(),
                                "Price": rest[3].strip()
                            })
    except FileNotFoundError:
        pass
    return orders


def save_new_order(name, location, main, side, drink, price):
    """Save a new order to both files."""
    # Format the order string
    full_order_parts = [main.upper()]
    if side:
        full_order_parts.append(side.upper())
    if drink:
        full_order_parts.append(drink.upper())
    full_order = ", ".join(full_order_parts)
    
    # Get timestamp
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to order_history.txt (append-only)
    with open(ORDERS_FILE, "a") as file:
        file.write(f"{timestamp_str}: {name.title()} | {location} | {full_order} | ${price:.2f}\n")
    
    # Save to prices.txt (append-only)
    with open(PRICES_FILE, "a") as file:
        file.write(f"{location} | {full_order} | ${price:.2f}\n")


def update_price(line_index, new_price):
    """Update the price of a specific line in prices.txt."""
    try:
        with open(PRICES_FILE, "r") as file:
            lines = file.readlines()
        
        if 0 <= line_index < len(lines):
            parts = lines[line_index].strip().split("|")
            if len(parts) == 3:
                location = parts[0].strip()
                full_order = parts[1].strip()
                lines[line_index] = f"{location} | {full_order} | ${new_price:.2f}\n"
                
                with open(PRICES_FILE, "w") as file:
                    file.writelines(lines)
                return True
    except FileNotFoundError:
        pass
    return False


def delete_orders_by_history_index(history_indices):
    """Delete multiple orders by their indices in order_history.txt from both files."""
    # Sort indices in reverse so we delete from highest to lowest (prevents index shifting)
    history_indices = sorted(history_indices, reverse=True)
    
    try:
        # Read order_history.txt to get the orders to delete
        with open(ORDERS_FILE, "r") as file:
            history_lines = file.readlines()
        
        orders_to_delete = []
        for idx in history_indices:
            if 0 <= idx < len(history_lines):
                line = history_lines[idx].strip()
                # Parse to get Location, Order, Price
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    rest = parts[1].split("|")
                    if len(rest) == 4:
                        orders_to_delete.append({
                            "location": rest[1].strip(),
                            "order": rest[2].strip(),
                            "price": rest[3].strip()
                        })
        
        # Delete from order_history.txt
        for idx in history_indices:
            if 0 <= idx < len(history_lines):
                history_lines.pop(idx)
        
        with open(ORDERS_FILE, "w") as file:
            file.writelines(history_lines)
        
        # Delete matching entries from prices.txt
        with open(PRICES_FILE, "r") as file:
            price_lines = file.readlines()
        
        # Remove lines that match the deleted orders (delete from highest index first)
        for order in orders_to_delete:
            price_lines = [line for line in price_lines if not (
                line.strip().split("|")[0].strip() == order["location"] and
                line.strip().split("|")[1].strip() == order["order"] and
                line.strip().split("|")[2].strip() == order["price"]
            )]
        
        with open(PRICES_FILE, "w") as file:
            file.writelines(price_lines)
        
        return True
    except FileNotFoundError:
        return False


# ==================== PAGE 1: ADD ORDER ====================

def page_add_order():
    st.title("📝 Add New Order")
    
    # Customer info
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Customer Name", placeholder="Enter customer name")
    with col2:
        location = st.text_input("Restaurant/Location", placeholder="Enter location")
    
    st.markdown("---")
    
    # Combo selector
    is_combo = st.checkbox("Is this a combo order?")
    
    if is_combo:
        col1, col2 = st.columns(2)
        with col1:
            main_item = st.text_input("Main Item", placeholder="e.g., Burger Combo")
        with col2:
            combo_price = st.number_input("Combo Price ($)", min_value=0.0, step=0.01, format="%.2f")
        side = ""
        drink = ""
        total_price = combo_price
    else:
        # Main item and price
        col1, col2 = st.columns(2)
        with col1:
            main_item = st.text_input("Main Item", placeholder="e.g., Burger")
        with col2:
            main_price = st.number_input("Main Price ($)", min_value=0.0, step=0.01, format="%.2f")
        
        # Side item and price
        col1, col2 = st.columns(2)
        with col1:
            side = st.text_input("Side Item (optional)", placeholder="e.g., Fries")
        with col2:
            side_price = st.number_input("Side Price ($)", min_value=0.0, step=0.01, format="%.2f")
        
        # Drink item and price
        col1, col2 = st.columns(2)
        with col1:
            drink = st.text_input("Drink (optional)", placeholder="e.g., Coke")
        with col2:
            drink_price = st.number_input("Drink Price ($)", min_value=0.0, step=0.01, format="%.2f")
        
        total_price = main_price + side_price + drink_price
    
    st.markdown("---")
    
    col_display1, col_display2 = st.columns(2)
    with col_display1:
        st.subheader("Order Summary")
        st.write(f"**Name:** {name if name else 'N/A'}")
        st.write(f"**Location:** {location if location else 'N/A'}")
        st.write(f"**Order Items:** {main_item if main_item else 'N/A'}")
        if side:
            st.write(f"  - Side: {side}")
        if drink:
            st.write(f"  - Drink: {drink}")
        st.write(f"**Total Price:** ${total_price:.2f}")
    
    with col_display2:
        submit_button = st.button("✅ Save Order", use_container_width=True)
        if submit_button:
            if not name or not location or not main_item:
                st.error("Please fill in all required fields: Name, Location, and Main Item")
            else:
                save_new_order(name, location, main_item, side, drink, total_price)
                st.success("✅ Order saved successfully!")
                st.balloons()


# ==================== PAGE 2: VIEW ORDERS ====================

def page_view_orders():
    st.title("👀 View All Orders")
    
    orders = read_order_history()
    
    if not orders:
        st.info("No orders found. Start by adding a new order!")
    else:
        df = pd.DataFrame(orders)
        # Sort by Location alphabetically
        df = df.sort_values(by="Location").reset_index(drop=True)
        
        st.subheader(f"Total Orders: {len(orders)}")
        
        # Initialize session state for checkboxes if not exists
        if "selected_orders" not in st.session_state:
            st.session_state.selected_orders = {i: False for i in range(len(df))}
        
        # Display table with checkboxes
        cols = st.columns([0.5, 1.5, 1.5, 1.5, 1.5, 1])
        cols[0].write("**Select**")
        cols[1].write("**Timestamp**")
        cols[2].write("**Name**")
        cols[3].write("**Location**")
        cols[4].write("**Order / Price**")
        
        for idx, row in df.iterrows():
            cols = st.columns([0.5, 1.5, 1.5, 1.5, 1.5, 1])
            st.session_state.selected_orders[idx] = cols[0].checkbox(
                label="Select",
                value=st.session_state.selected_orders.get(idx, False),
                key=f"checkbox_{idx}",
                label_visibility="collapsed"
            )
            cols[1].write(row["Timestamp"])
            cols[2].write(row["Name"])
            cols[3].write(row["Location"])
            cols[4].write(f"{row['Order']} / {row['Price']}")
        
        st.markdown("---")
        
        # Calculate statistics
        col1, col2, col3 = st.columns(3)
        prices = [float(order["Price"].replace("$", "")) for order in orders]
        
        with col1:
            st.metric("Average Order Price", f"${sum(prices) / len(prices):.2f}")
        with col2:
            st.metric("Highest Order", f"${max(prices):.2f}")
        with col3:
            st.metric("Lowest Order", f"${min(prices):.2f}")
        
        st.markdown("---")
        
        # Delete button
        selected_indices = [idx for idx, selected in st.session_state.selected_orders.items() if selected]
        delete_disabled = len(selected_indices) == 0
        
        if st.button(
            f"🗑️ Delete Selected Orders ({len(selected_indices)})",
            disabled=delete_disabled,
            use_container_width=True,
            type="secondary"
        ):
            if delete_orders_by_history_index(selected_indices):
                st.success(f"✅ {len(selected_indices)} order(s) deleted successfully!")
                st.session_state.selected_orders = {}
                st.rerun()
            else:
                st.error("Failed to delete orders")


# ==================== PAGE 3: UPDATE/DELETE ORDERS ====================

def page_update_prices():
    st.title("✏️ Update Prices")
    
    orders = read_prices_file()
    
    if not orders:
        st.info("No orders found. Start by adding a new order!")
        return
    
    st.subheader("Select an order to update the price")
    
    # Create a display dataframe with row numbers (narrow)
    df = pd.DataFrame(orders)
    df.insert(0, "No.", range(1, len(df) + 1))
    display_df = df[["No.", "Location", "Order", "Price"]]
    
    # Use column config to make No. column narrower
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No.": st.column_config.NumberColumn(
                "No.",
                width="small"
            )
        }
    )
    
    st.markdown("---")
    
    # Selection section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_index = st.number_input(
            "Select order number to update (1-indexed):",
            min_value=1,
            max_value=len(orders),
            value=1
        )
        actual_index = selected_index - 1
    
    if actual_index < len(orders):
        selected_order = orders[actual_index]
        
        st.markdown("---")
        st.subheader("Selected Order")
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.write(f"**Location:** {selected_order['Location']}")
        with col_info2:
            st.write(f"**Order:** {selected_order['Order']}")
        with col_info3:
            st.write(f"**Price:** {selected_order['Price']}")
        
        st.markdown("---")
        st.subheader("Update Price")
        old_price = float(selected_order['Price'].replace("$", ""))
        new_price = st.number_input(
            "New Price ($)",
            min_value=0.0,
            value=old_price,
            step=0.01,
            format="%.2f"
        )
        
        if st.button("💾 Update Price", use_container_width=True):
            if update_price(actual_index, new_price):
                st.success(f"✅ Price updated from ${old_price:.2f} to ${new_price:.2f}")
                st.rerun()
            else:
                st.error("Failed to update price")


# ==================== MAIN APP ====================

def main():
    # Sidebar navigation
    st.sidebar.title("📋 Order Tracker")
    page = st.sidebar.radio(
        "Navigation",
        ["Add Order", "View Orders", "Update Prices"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **How to use:**
        - **Add Order**: Create and save new orders
        - **View Orders**: See all orders and delete as needed
        - **Update Prices**: Edit order prices
        """
    )
    
    # Route to appropriate page
    if page == "Add Order":
        page_add_order()
    elif page == "View Orders":
        page_view_orders()
    elif page == "Update Prices":
        page_update_prices()


if __name__ == "__main__":
    main()

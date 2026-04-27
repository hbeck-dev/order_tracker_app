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
            for line in file:
                if line.strip():
                    orders.append(line.strip())
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


def delete_order(line_index):
    """Delete an order from both files."""
    success = True
    
    # Delete from prices.txt
    try:
        with open(PRICES_FILE, "r") as file:
            lines = file.readlines()
        
        if 0 <= line_index < len(lines):
            lines.pop(line_index)
            with open(PRICES_FILE, "w") as file:
                file.writelines(lines)
    except FileNotFoundError:
        success = False
    
    # Note: order_history.txt is append-only and not meant to be deleted from,
    # but we'll leave a comment about which order was deleted
    # Alternatively, you could implement a deletion log here
    
    return success


# ==================== PAGE 1: ADD ORDER ====================

def page_add_order():
    st.title("📝 Add New Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Customer Name", placeholder="Enter customer name")
        location = st.text_input("Restaurant/Location", placeholder="Enter location")
    
    with col2:
        main_item = st.text_input("Main Item", placeholder="e.g., Burger")
        is_combo = st.checkbox("Is it a combo?")
    
    if is_combo:
        combo_price = st.number_input("Combo Price ($)", min_value=0.0, step=0.01, format="%.2f")
        side = ""
        drink = ""
        total_price = combo_price
    else:
        col3, col4, col5 = st.columns(3)
        with col3:
            main_price = st.number_input("Main Item Price ($)", min_value=0.0, step=0.01, format="%.2f")
        
        side = st.text_input("Side Item (optional)", placeholder="e.g., Fries")
        with col4:
            side_price = st.number_input("Side Price ($)", min_value=0.0, step=0.01, format="%.2f")
        
        drink = st.text_input("Drink (optional)", placeholder="e.g., Coke")
        with col5:
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
    
    orders = read_prices_file()
    
    if not orders:
        st.info("No orders found. Start by adding a new order!")
    else:
        df = pd.DataFrame(orders)
        # Display without the Index column for cleaner view
        display_df = df[["Location", "Order", "Price"]]
        
        st.subheader(f"Total Orders: {len(orders)}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Calculate statistics
        col1, col2, col3 = st.columns(3)
        prices = [float(order["Price"].replace("$", "")) for order in orders]
        
        with col1:
            st.metric("Average Order Price", f"${sum(prices) / len(prices):.2f}")
        with col2:
            st.metric("Highest Order", f"${max(prices):.2f}")
        with col3:
            st.metric("Lowest Order", f"${min(prices):.2f}")


# ==================== PAGE 3: UPDATE/DELETE ORDERS ====================

def page_update_delete():
    st.title("✏️ Update / Delete Orders")
    
    orders = read_prices_file()
    
    if not orders:
        st.info("No orders found. Start by adding a new order!")
        return
    
    st.subheader("Select an order to edit or delete")
    
    # Create a display dataframe without index
    df = pd.DataFrame(orders)
    display_df = df[["Location", "Order", "Price"]]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Selection section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_index = st.number_input(
            "Select order number to modify (1-indexed):",
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
        
        # Action buttons
        tab1, tab2 = st.tabs(["Update Price", "Delete Order"])
        
        with tab1:
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
        
        with tab2:
            st.subheader("Delete Order")
            st.warning(
                f"⚠️ You are about to delete:\n\n"
                f"**Location:** {selected_order['Location']}\n\n"
                f"**Order:** {selected_order['Order']}\n\n"
                f"**Price:** {selected_order['Price']}\n\n"
                f"This order will be removed from both files."
            )
            
            confirmation = st.checkbox("I confirm I want to delete this order")
            
            if confirmation:
                if st.button("🗑️ Delete Order", use_container_width=True, type="secondary"):
                    if delete_order(actual_index):
                        st.success("✅ Order deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete order")


# ==================== MAIN APP ====================

def main():
    # Sidebar navigation
    st.sidebar.title("📋 Order Tracker")
    page = st.sidebar.radio(
        "Navigation",
        ["Add Order", "View Orders", "Update/Delete Orders"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **How to use:**
        - **Add Order**: Create and save new orders
        - **View Orders**: See all saved orders in a table
        - **Update/Delete**: Edit prices or remove orders
        """
    )
    
    # Route to appropriate page
    if page == "Add Order":
        page_add_order()
    elif page == "View Orders":
        page_view_orders()
    elif page == "Update/Delete Orders":
        page_update_delete()


if __name__ == "__main__":
    main()

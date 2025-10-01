"""
Stock search and product identification service.
"""

import datetime
from utils.date_utils import parse_date, format_date


def _get_product_for_action(query, all_stock_data):
    """Find a product by query string in stock data."""
    query_lower = query.lower().strip()
    potential_products = {}

    for carton in all_stock_data:
        if carton['product_id'].lower() == query_lower:
            potential_products[carton['product_id']] = carton['product_name']
            break
    
    if not potential_products:
        for carton in all_stock_data:
            if query_lower in carton['product_name'].lower() or \
               carton['product_name'].lower() in query_lower:
                potential_products[carton['product_id']] = carton['product_name']

    if not potential_products:
        return None, None, f"Sorry, I couldn't find any stock matching '{query}'. Please try a different name or ID."
    elif len(potential_products) > 1:
        matched_names = [f"{pid} ({pname})" for pid, pname in potential_products.items()]
        return None, None, f"I found multiple products matching '{query}': {', '.join(matched_names)}. Please be more specific or provide the exact Product ID."
    else:
        product_id = list(potential_products.keys())[0]
        product_name = potential_products[product_id]
        return product_id, product_name, ''


def get_product_summary_text(query, all_stock_data):
    """Get a detailed summary of a product's stock status."""
    product_id_found, product_name_found, identification_message = _get_product_for_action(query, all_stock_data)

    if not product_id_found:
        return identification_message

    found_cartons = [carton for carton in all_stock_data if carton['product_id'] == product_id_found]

    # Collect all unique MRPs for this product
    unique_mrps = sorted(set([carton.get('mrp', 0) for carton in found_cartons if carton.get('mrp') is not None]))
    mrp_text = ''
    if unique_mrps:
        if len(unique_mrps) == 1:
            mrp_text = f"MRP: ₹{unique_mrps[0]:.2f}"
        else:
            mrp_text = "MRPs: " + ", ".join([f"₹{mrp:.2f}" for mrp in unique_mrps])

    total_live_units = 0
    total_damaged_units = 0
    total_expired_units = 0
    unique_locations = set()
    active_carton_details = []
    outwarded_cartons_info = []

    oldest_inwarded_date = datetime.date(9999, 12, 31)
    oldest_inwarded_carton_id = None
    nearest_expiry_date = datetime.date(9999, 12, 31)
    nearest_expiry_carton_id = None

    current_date = datetime.date.today()

    for carton in found_cartons:
        unique_locations.add(carton['location'])

        if carton['date_outwarded'] is None:
            is_expired = False
            if carton['expiry_date']:
                try:
                    expiry_date_obj = parse_date(carton['expiry_date'])
                    if expiry_date_obj and expiry_date_obj <= current_date:
                        is_expired = True
                        total_expired_units += carton['quantity_per_carton']
                    elif expiry_date_obj and expiry_date_obj < nearest_expiry_date:
                        nearest_expiry_date = expiry_date_obj
                        nearest_expiry_carton_id = carton['carton_id']
                except (TypeError, ValueError):
                    pass
            
            if is_expired:
                total_damaged_units += carton['quantity_per_carton']
            else:
                total_live_units += carton['quantity_per_carton']
                total_damaged_units += carton['damaged_units']

            active_carton_details.append({
                'carton_id': carton['carton_id'],
                'quantity_per_carton': carton['quantity_per_carton'],
                'damaged_units': carton['damaged_units'],
                'date_inwarded': carton['date_inwarded'],
                'expiry_date': carton['expiry_date'],
                'is_expired': is_expired,
            })

            if not is_expired:
                inward_date_obj = parse_date(carton['date_inwarded'])
                if inward_date_obj and inward_date_obj < oldest_inwarded_date:
                    oldest_inwarded_date = inward_date_obj
                    oldest_inwarded_carton_id = carton['carton_id']
        else:
            outwarded_cartons_info.append(carton['carton_id'])

    summary_lines = []
    summary_lines.append(f"Searching for {product_name_found} ({product_id_found}).\n")
    if mrp_text:
        summary_lines.append(mrp_text)
    summary_lines.append("---")
    summary_lines.append(f"Total Live Sellable Stock: {total_live_units} units (across {len([c for c in active_carton_details if not c['is_expired']])} active non-expired carton(s)).")
    summary_lines.append(f"Total Damaged/Expired Stock: {total_damaged_units} units ({total_expired_units} expired, {total_damaged_units - total_expired_units} physically damaged).")
    summary_lines.append(f"Locations: {', '.join(sorted(list(unique_locations)))}")

    if active_carton_details:
        summary_lines.append("\nCarton Details (Live Stock):")
        active_carton_details.sort(key=lambda x: (
            parse_date(x['expiry_date']) or datetime.date(9999, 12, 31),
            parse_date(x['date_inwarded']) or datetime.date(1, 1, 1)
        ))

        for detail in active_carton_details:
            qty_status = f"{detail['quantity_per_carton']} units"
            if detail['damaged_units'] > 0:
                qty_status += f" ({detail['damaged_units']} physically damaged)"
            
            carton_remarks = []
            if detail['is_expired']:
                carton_remarks.append("EXPIRED")
            
            remark_text = f" ({', '.join(carton_remarks)})" if carton_remarks else ""

            summary_lines.append(
                f"  - Carton {detail['carton_id']}: {qty_status}{remark_text}. " +
                f"Inwarded: {detail['date_inwarded']}. " +
                f"Expires: {detail['expiry_date'] or 'N/A'}."
            )
    
    remarks = []
    if oldest_inwarded_carton_id and oldest_inwarded_date != datetime.date(9999, 12, 31):
        days_old = (current_date - oldest_inwarded_date).days
        if days_old > 90:
            remarks.append(f"Carton {oldest_inwarded_carton_id} (Inwarded: {format_date(oldest_inwarded_date)}) is older stock. Consider prioritizing its sale (FIFO).")
        else:
            remarks.append(f"The oldest active sellable stock is Carton {oldest_inwarded_carton_id} (Inwarded: {format_date(oldest_inwarded_date)}).")
    
    if nearest_expiry_carton_id and nearest_expiry_date != datetime.date(9999, 12, 31):
        days_to_expiry = (nearest_expiry_date - current_date).days
        if days_to_expiry <= 0:
            pass
        elif days_to_expiry <= 60:
            remarks.append(f"URGENT! Carton {nearest_expiry_carton_id} expires on {format_date(nearest_expiry_date)} (in {days_to_expiry} days). Prioritize selling this carton (FEFO).")
        elif days_to_expiry <= 180:
            remarks.append(f"Warning: Carton {nearest_expiry_carton_id} expires on {format_date(nearest_expiry_date)} (in {days_to_expiry} days). Keep an eye on this stock.")
        else:
            remarks.append(f"The earliest expiring active sellable stock is Carton {nearest_expiry_carton_id} (Expires: {format_date(nearest_expiry_date)}).")
        
    if outwarded_cartons_info:
        remarks.append(f"Some cartons ({', '.join(outwarded_cartons_info)}) of this product have been outwarded previously.")

    if remarks:
        summary_lines.append("\nRemarks:")
        summary_lines.extend([f"  - {r}" for r in remarks])

    return "\n".join(summary_lines)
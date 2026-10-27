# Medical-store-management-tracker-using-cli
SHORT DESCRIPTION:
A command-line Medical Store Management System built in Python to manage medicine stock (with a 25% reorder calculator), batch expiry dates, and sales revenue and profit using CSV file storage.

FEATURES:

Morning Dashboard: Shows medicines below the 25% reorder level, the 3 nearest batch expiry dates, and total revenue and profit so far.
Stock & Reorder Tracker: Registers medicines, receives new batches and calculates how many units you can safely sell or must restock to stay at 25% of shelf capacity.
Expiry Tracker: Adds batches with YYYY-MM-DD expiry dates, sorts active batches by expiry, flags expired or soon-to-expire stock, and disposes of batches (removing their units from stock).
Sales & Profit Calculator: Records sales, blocks overselling, and calculates revenue, profit and profit margin for each medicine and for the whole store.
Medicine Deep Dive: Displays complete stock status, active batches and sales totals for any selected medicine.

DATA STRUCTURES AND ALGORITHMS USED:

2D Lists (Dynamic Arrays): Used to load, access, and update rows from CSV files in memory.
Dictionaries (Hash Maps): Used to group sales by medicine, join Sales with Medicines in linear time for revenue and profit, and dispatch menu choices.
Tuples: Used to map filtered active batches back to their original row index, and to store each sale as (date, quantity).
Iterative Simulation: Used to test unit-by-unit stock changes around the 25% reorder threshold, using integer comparisons.
Timsort (Custom Key Sorting): Used to sort active batches chronologically by expiry date.

CSV FILES AUTOMATICALLY CREATED:

Medicines.csv (Medicine_Name, Selling_Price, Cost_Price, Stock, Max_Stock)
Batches.csv (Medicine_Name, Batch_No, Expiry_Date, Quantity, Status)
Sales.csv (Medicine_Name, Sale_Date, Qty_Sold)

HOW TO RUN:

Make sure Python 3 is installed on your computer.
Open a terminal or command prompt in the project folder.
Run the command: python medical_store_manager.py

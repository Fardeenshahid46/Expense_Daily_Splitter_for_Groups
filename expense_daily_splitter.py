import tkinter as tk
from tkinter import messagebox,ttk
import json
import os

class ExpenseSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Splitter for Groups")
        self.root.configure(bg="lightyellow")
        self.participant_list = []
        self.expense_data= []

        self.setup_ui()
        self.load_data()  

    def setup_ui(self):
        # Section: To add Members
        member_frame = tk.LabelFrame(self.root, text="Group Members 👥", padx=10, pady=10,bg="lightyellow")
        member_frame.pack(padx=10, pady=5, fill="x")

        self.member_entry = tk.Entry(member_frame)
        self.member_entry.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(member_frame, text="Add Member", command=self.add_member).pack(side="left", padx=5)

        # Section: Entry of Expenses
        expense_frame = tk.LabelFrame(self.root, text="Add Expense", padx=10, pady=10,bg="lightyellow")
        expense_frame.pack(padx=10, pady=5, fill="x")

        self.payer_dropdown = ttk.Combobox(expense_frame, values=self.participant_list, state="readonly")
        self.payer_dropdown.set("Select Payer")
        self.payer_dropdown.pack(side="left", padx=5)
        self.input_amount = tk.Entry(expense_frame)
        self.input_amount.pack(side="left", padx=5)
        self.input_amount.insert(0, "Enter Amount in Rs:")
        tk.Button(self.root, text="Show Final Balance 🔍", command=self.calculate_split).pack(pady=10)
       
        tk.Button(expense_frame, text="Add Expense", command=self.add_expense).pack(side="left", padx=5)

        #Section:Summary Display
        summary_frame = tk.LabelFrame(self.root, text="Expense Summary", padx=10, pady=10,bg="lightyellow")
        summary_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.summary_area = tk.Text(summary_frame, height=10)
        self.summary_area.pack(fill="both", expand=True)

        # Action Buttons
        tk.Button(self.root, text="Calculate Who Owes Whom", command=self.calculate_split).pack(pady=10)
        tk.Button(self.root, text="Reset All Data 🧹", command=self.reset_all).pack(pady=5) 
    def reset_all(self):
          if messagebox.askyesno("Reset", "Do you want to delete all your data?"):
            self.participant_list.clear()
            self.expense_data.clear()
            self.payer_dropdown.set("Select Payer")
            self.payer_dropdown['values'] = []
            self.summary_area.delete(1.0, tk.END)
            self.member_entry.delete(0, tk.END)
            self.input_amount.delete(0, tk.END)
            self.input_amount.insert(0, "Enter Amount in Rs:")

        #To clear the file content instead of deleting
            try:
                with open("expense_daily_splitter.json", "w") as f:
                    json.dump({"members": [], "expenses": []}, f, indent=4)
            except Exception as e:
                   messagebox.showerror("File Error", f"Couldn't reset file: {e}")
                   return

            messagebox.showinfo("Reset", "All data has been cleared.")
               
    #This function add members
    def add_member(self):
        name = self.member_entry.get().strip()
        if name and name not in self.participant_list:
            self.participant_list.append(name)
            self.payer_dropdown['values'] = self.participant_list
            self.member_entry.delete(0, tk.END)
            self.save_data()
            messagebox.showinfo("Member Added", f"{name} has been added to the group.")
        else:
            messagebox.showerror("Error", "Invalid or duplicate name.")
            
    #This function add expense of a member
    def add_expense(self):
        payer = self.payer_dropdown.get()
        try:
            amount = float(self.input_amount.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        if payer not in self.participant_list or amount <= 0:
            messagebox.showerror("Error", "Please enter valid payer and amount.")
            return

        self.expense_data.append({"payer": payer, "amount": amount})
        self.input_amount.delete(0, tk.END)
        self.input_amount.insert(0, "Amount")
        self.payer_dropdown.set("Select Payer")
        self.save_data()
        messagebox.showinfo("Expense Added", f"{payer} paid Rs.{amount}")
    
    #To show balance
    def calculate_split(self):
        n = len(self.participant_list)
        if n == 0 or not self.expense_data:
            messagebox.showwarning("Missing Data", "Add members and expenses first.")
            return

        total_spent = sum(e["amount"] for e in self.expense_data)
        equal_share = total_spent / n

        paid_dict = {member: 0 for member in self.participant_list}
        for e in self.expense_data:
            paid_dict[e["payer"]] += e["amount"]

        balance_dict = {member: round(paid_dict[member] - equal_share, 2) for member in self.participant_list}

        #To set logic
        creditors = [(m, b) for m, b in balance_dict.items() if b > 0]
        debtors = [(m, b) for m, b in balance_dict.items() if b < 0]

        i, j = 0, 0
        result = []

        while i < len(debtors) and j < len(creditors):
            debtor, debt = debtors[i]
            creditor, credit = creditors[j]

            settle_amount = min(-debt, credit)
            result.append(f"{debtor} owes {creditor} Rs.{settle_amount}")

            debt += settle_amount
            credit -= settle_amount

            if round(debt, 2) == 0:
                i += 1
            else:
                debtors[i] = (debtor, debt)

            if round(credit, 2) == 0:
                j += 1
            else:
                creditors[j] = (creditor, credit)

        #Display the result in GUI
        self.summary_area.delete(1.0, tk.END)
        self.summary_area.insert(tk.END, f"Total Spent: Rs.{total_spent}\n")
        self.summary_area.insert(tk.END, f"Each Person Should Pay: Rs.{round(equal_share, 2)}\n\n")
        for line in result:
            self.summary_area.insert(tk.END, line + "\n")

    def save_data(self):
        data = {
            "members": self.participant_list,
            "expenses": self.expense_data
        }
        try:
            with open("expense_daily_splitter.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_data(self):
        #If the file doesn't exist so pre-fill
        if os.path.exists("expense_daily_splitter.json"):
            try:
                with open("expense_daily_splitter.json", "r") as f:
                    data = json.load(f)
                    self.participant_list = data.get("members", [])
                    self.expense_data = data.get("expenses", [])
                    self.payer_dropdown['values'] = self.participant_list
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

# To run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseSplitterApp(root)
    root.mainloop()

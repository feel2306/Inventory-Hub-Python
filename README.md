# 📦 Inventory Hub — Python Edition

A desktop-style inventory management web app built with **Python**, **Streamlit**, and **SQLite3**. Manage your stock, track sales, monitor profits, and get expiry & low-stock alerts — all in one place.

---

## 🚀 Features

- 🔐 **Authentication** — Register, Login, and Forgot Password (via mobile number)
- 📦 **Available Stock** — View full inventory with expiry alerts and low stock warnings
- 📥 **Stock Entry** — Add new items with quantity, buying/selling price, and expiry date
- 🛒 **Sell Items** — Record sales with automatic stock deduction
- ✏️ **Update Price** — Update selling price (must be greater than buying price)
- 🗑️ **Delete Items** — Remove items from inventory via dropdown
- 📊 **Analysis** — Daily sales & profit charts powered by Plotly (bar charts)
- 👤 **Profile** — View profile, update name/mobile, and logout

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3 |
| UI Framework | Streamlit |
| Database | SQLite3 (local file) |
| Charts | Plotly Express |
| Data Handling | Pandas |

---

## 📁 Project Structure

```
inventory-hub-python/
│
├── inv.py              # Main application file (all pages & logic)
├── inv_hub.db          # SQLite3 database (auto-created on first run)
├── Inhub.png           # App logo / favicon
└── requirements.txt    # Python dependencies
```

---

## 🗄️ Database Schema

### `users`
| Column | Type | Description |
|--------|------|-------------|
| u_id | INTEGER (PK) | Auto-incremented user ID |
| u_name | TEXT | Unique username |
| pass | TEXT | User password |
| mobile | TEXT | Registered mobile number |

### `inventory`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Auto-incremented item ID |
| user_id | INTEGER (FK) | References users.u_id |
| item_name | TEXT | Name of the item |
| quantity | INTEGER | Stock quantity |
| sell_price | REAL | Selling price |
| buying_price | REAL | Buying price |
| exp_date | DATE | Expiry date |
| arrival_date | DATE | Date item was added |
| profit | REAL | Profit per unit (sell - buy) |

### `sales`
| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER (FK) | References users.u_id |
| item_name | TEXT | Name of sold item |
| quantity | INTEGER | Quantity sold |
| date_sold | DATE | Date of sale |
| net_profit | REAL | Total profit from the sale |

---

## 🔑 Password Requirements

When registering or resetting password:
- Must be **at least 6 characters**
- Must **start with a letter**
- Must contain at least **one digit**
- Must contain at least **one special character**

---

## ⚠️ Known Limitations

- Passwords are stored as plain text — not recommended for production use
- SQLite is a local file-based database, not suitable for multi-user deployment
- No session timeout — user stays logged in until they manually logout

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

Built by **[Feel]**

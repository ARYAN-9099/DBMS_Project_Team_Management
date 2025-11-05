# 🚀 QUICK START GUIDE - Esports Management System

## ⚡ 5-Minute Setup

### 1️⃣ Prerequisites Check
```powershell
# Check Python version (need 3.8+)
python --version

# Check MySQL is running
mysql --version
```

### 2️⃣ Install & Setup
```powershell
# Navigate to project folder
cd c:\coding_projects\DBMS_Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Database Setup
```command prompt
# Import database (from project folder)
mysql -u root -p < esports_db.sql

# Enter your MySQL password when prompted
```

### 4️⃣ Configure Database Connection

Edit `app.py` - Update lines 32-36:
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'           # YOUR USERNAME
app.config['MYSQL_PASSWORD'] = 'your_pass'   # YOUR PASSWORD
app.config['MYSQL_DB'] = 'esports_db'
```

### 5️⃣ Run Application
```powershell
python app.py
```

### 6️⃣ Access System
Open browser: **http://localhost:5000**

---

## 🎮 Test the System

### Pre-loaded Test Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@esports.com | admin123 | Admin |
| john@example.com | pass123 | Organizer |
| alice@example.com | pass123 | Player |

### Quick Test Flow

1. **Login** with `admin@esports.com` / `admin123`
2. **View Tournaments** - See 5 pre-loaded tournaments
3. **Check Leaderboard** - Click on "Dota Pro Circuit" (Tournament #4)
4. **View Teams** - See 5 teams with statistics
5. **Record a Match** - Try recording a new match result
6. **Check Updated Leaderboard** - See real-time updates

---

## 📊 Pre-loaded Sample Data

✅ **15 Users** (mix of players, organizers, admin)  
✅ **5 Teams** with complete rosters  
✅ **5 Games** (CS2, League of Legends, Valorant, Dota 2, Rocket League)  
✅ **5 Tournaments** (Upcoming, Ongoing, Completed)  
✅ **13 Matches** with scores and results  

---

## 🔍 Key Features to Demonstrate

### 1. Complex SQL Queries
- **Top Teams by Average Score**  
  Visit: `/api/top_teams` (JSON response)

- **Tournament Leaderboard**  
  Visit: `/leaderboard/4` (See Dota Pro Circuit standings)

### 2. Stored Procedure in Action
- **Record Match**  
  Go to: "Record Match" → Fill form  
  Backend calls `record_match_result` stored procedure

### 3. Trigger Demonstration
- **Duplicate Registration Prevention**  
  Try registering same team twice for a tournament  
  Trigger blocks it with error message

### 4. Database Views
- **Tournament Leaderboard View**  
  Automatically used in leaderboard pages

- **Team Performance Summary**  
  Shown in "All Teams" page

---

## 🛠️ Common Commands

### Start MySQL Service
```powershell
net start MySQL80
```

### Stop Application
Press `Ctrl+C` in terminal

### Check Database
```powershell
mysql -u root -p
mysql> USE esports_db;
mysql> SHOW TABLES;
mysql> SELECT * FROM teams;
```

### Reset Database
```powershell
# Re-import SQL file to reset all data
mysql -u root -p < esports_db.sql
```

---

## 📝 Project Report Checklist

For your college project report, include:

- [x] ER Diagram (can be created from schema)
- [x] Database Schema (all 8 tables documented)
- [x] Complex SQL Queries (7 queries provided)
- [x] Stored Procedures (2 procedures with explanation)
- [x] Triggers (3 triggers with logic)
- [x] Views (2 views with purpose)
- [x] Application Screenshots (capture all pages)
- [x] Code Documentation (all files heavily commented)
- [x] Testing Results (use pre-loaded data)
- [x] Future Enhancements (listed in README)

---

## 🎯 Demonstration Script

### For Project Presentation:

**1. Introduction (2 min)**
- Show home page
- Explain project objectives

**2. Database Features (3 min)**
- Open MySQL Workbench
- Show tables structure
- Demonstrate stored procedure call
- Show trigger in action

**3. Application Features (5 min)**
- User registration/login
- Create team
- Create tournament
- Register team for tournament
- Record match (uses stored procedure)
- Show updated leaderboard (uses view)

**4. Complex Queries (3 min)**
- Top 5 teams by average score
- Win/Loss ratio calculations
- Tournament history for a team

**5. Q&A (2 min)**
- Be ready to explain design decisions
- Discuss normalization (3NF)
- Explain indexing choices

---

## ⚠️ Troubleshooting Quick Fixes

### "Module 'flask_mysqldb' not found"
```powershell
pip install flask-mysqldb
```

### "Access denied for user 'root'@'localhost'"
Update password in `app.py` line 35

### "Database 'esports_db' doesn't exist"
```powershell
mysql -u root -p < esports_db.sql
```

### "Port 5000 already in use"
Change port in `app.py` line 677:
```python
app.run(debug=True, port=5001)
```

---

## 📱 Next Steps

After basic setup works:

1. ✅ Test all routes manually
2. ✅ Try API endpoints in browser
3. ✅ Record some test matches
4. ✅ Check leaderboard updates
5. ✅ Take screenshots for report
6. ✅ Prepare presentation
7. ✅ Add your own test data

---

## 💡 Pro Tips

- **Use Bootstrap Icons**: Already included via CDN
- **Check Browser Console**: F12 for any JavaScript errors
- **Test with Different Browsers**: Chrome, Firefox, Edge
- **Mobile Responsive**: Test on phone browser
- **Print Leaderboards**: Good for report appendix

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review code comments in `app.py`
3. Examine SQL file comments for query explanations
4. Test with pre-loaded data first

---

**Project Status**: ✅ Complete and Ready for Submission

**Estimated Setup Time**: 5-10 minutes  
**Estimated Demo Time**: 10-15 minutes  

Good luck with your project! 🎓🚀

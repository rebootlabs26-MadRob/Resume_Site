# SCHOOL & LEARNING - Python Mastery for Rob
## Hands-On, Visual, Practical Learning Plan

**Your Learning Profile:**
- Learning disabilities - struggle with traditional classroom settings
- Memory challenges - need to DO things to remember them
- Visual learner - need to SEE results immediately
- Hands-on style - learn by building, not reading
- Avoids crowds/people - prefer solo, focused work
- 20 years hardware experience - understand systems deeply

**Goal:** Master Python through YOUR projects, not textbook exercises.

---

## 🎯 LEARNING PHILOSOPHY

**Traditional Method (Doesn't Work for You):**
❌ Read chapter → Do practice problems → Take quiz → Forget everything

**YOUR Method (Works):**
✅ Have a real problem → Google/experiment → Build solution → Keep using it → Never forget

**So we're doing it YOUR way.**

---

## 📚 PHASE 1: FOUNDATION THROUGH YOUR CODE (Week 1-2)

### Day 1-2: Understand What You've Already Built

**Open Your Existing Projects:**
- `hardware_collector.py`
- `multi_ai_chat.py`
- `THISONEWORKSSAVE.py`
- Any DiagTool versions

**Exercise: Code Archaeology**

Pick ONE file you wrote. Read it line by line and answer:
1. What does this line do?
2. Why did I write it this way?
3. Could I explain this to someone else?

**When you hit something you don't understand:**
- Google: "python [specific thing] explained simply"
- Run JUST that line in Python interactive mode
- Change one thing and see what breaks

**Goal: Understand your OWN code before learning new stuff**

---

### Day 3-5: Python Interactive Mode (Your Sandbox)

**Open PowerShell, type:** `python`

Now you're in interactive Python - instant feedback, no files needed.

**Experiment Session #1: Variables & Data Types**

Type these, see what happens:
```python
# Numbers
x = 10
y = 3.14
print(x + y)

# Text (strings)
name = "Rob"
print(f"Hello {name}")

# Lists (collections)
tools = ["screwdriver", "multimeter", "laptop"]
print(tools[0])  # First tool
tools.append("soldering iron")
print(tools)

# True/False (booleans)
is_working = True
if is_working:
    print("System online")
```

**YOUR Task:** 
Replace my examples with YOUR hardware tools, YOUR projects, YOUR actual data.

**Why This Works:** You're not learning abstract concepts - you're describing YOUR world in code.

---

### Day 6-7: Functions (Reusable Code Chunks)

**Concept:** You do the same tasks repeatedly (check voltage, test component, etc.)
Functions = Save those tasks so you don't repeat yourself

**Your First Function - Hardware Tester:**

```python
def test_component(component_name, voltage):
    """Test if a component is working"""
    print(f"Testing {component_name}...")
    
    if voltage > 5:
        return "PASS - Voltage good"
    else:
        return "FAIL - Voltage too low"

# Use it
result = test_component("Power Supply", 12)
print(result)

result = test_component("Battery", 3.2)
print(result)
```

**Exercise:** Write a function for something YOU actually do:
- Check device model
- Calculate repair cost
- Determine if device is worth fixing

**Rule:** If you do it more than twice, make it a function.

---

## 🛠️ PHASE 2: BUILD REAL TOOLS (Week 3-4)

### Project 1: Device Inventory Manager

**What You're Building:**
A simple program to track all the devices you work on.

**Skills You'll Learn:**
- File handling (save/load data)
- Lists and dictionaries
- User input
- Basic error handling

**Step-by-Step:**

```python
# inventory.py

devices = []

def add_device():
    """Add a new device to inventory"""
    print("\n--- Add Device ---")
    brand = input("Brand: ")
    model = input("Model: ")
    issue = input("Issue: ")
    
    device = {
        "brand": brand,
        "model": model,
        "issue": issue,
        "status": "In Progress"
    }
    
    devices.append(device)
    print(f"✓ Added {brand} {model}")

def list_devices():
    """Show all devices"""
    print("\n--- Device Inventory ---")
    if not devices:
        print("No devices yet")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device['brand']} {device['model']} - {device['status']}")
        print(f"   Issue: {device['issue']}")

def main():
    """Main program loop"""
    while True:
        print("\n=== Device Tracker ===")
        print("1. Add device")
        print("2. List devices")
        print("3. Quit")
        
        choice = input("\nChoice: ")
        
        if choice == "1":
            add_device()
        elif choice == "2":
            list_devices()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
```

**Your Assignment:**
1. Type this code (don't copy/paste - typing helps memory)
2. Run it, test it
3. Add ONE feature:
   - Save devices to a file
   - Mark device as complete
   - Calculate total repair time
   - Your choice!

**Why This Works:** You're building something YOU'LL ACTUALLY USE.

---

### Project 2: Diagnostic Checklist Automation

**What You're Building:**
Script that walks you through device diagnostics step-by-step.

**Your Hardware Workflow:**
1. Check power
2. Check display
3. Check ports
4. Check storage
5. Document findings

**In Python:**

```python
# diagnostic.py

def run_diagnostic(device_name):
    """Run diagnostic checklist"""
    print(f"\n=== Diagnosing: {device_name} ===\n")
    
    checks = [
        "Power button responds",
        "Display lights up",
        "USB ports functional",
        "Storage detected",
        "No physical damage"
    ]
    
    results = {}
    
    for check in checks:
        response = input(f"{check}? (y/n): ").lower()
        results[check] = (response == 'y')
    
    # Summary
    print("\n--- Results ---")
    passed = sum(results.values())
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    for check, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}")
    
    # Recommendation
    if passed == total:
        print("\n→ Device is functional")
    elif passed >= total * 0.7:
        print("\n→ Minor repairs needed")
    else:
        print("\n→ Major repairs required")

# Run it
device = input("Enter device name: ")
run_diagnostic(device)
```

**Your Assignment:**
Customize this for YOUR actual diagnostic process. Add your real steps.

---

## 🎨 PHASE 3: GUI TOOLS (Week 5-6)

**You've built:** SkullGUI, PyQt5 DiagTool

**Let's understand HOW they work, then build a simpler one.**

### Understanding Your SkullGUI

Open: `Edits/SkullGUI/SkullGUI_DiagTool.py`

**Find these sections (I'll explain each):**

```python
# This creates the window
app = QApplication(sys.argv)
window = QMainWindow()

# This adds a button
button = QPushButton("Click Me")

# This runs when button is clicked
def on_click():
    print("Button pressed!")
button.clicked.connect(on_click)
```

**Exercise: Minimal GUI**

```python
# simple_gui.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

def create_window():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Rob's Tool")
    window.setGeometry(100, 100, 400, 300)
    
    # Central widget
    central = QWidget()
    layout = QVBoxLayout()
    
    # Label
    label = QLabel("Device Status: Unknown")
    layout.addWidget(label)
    
    # Button
    def check_device():
        label.setText("Device Status: Checking...")
        # Your actual check code here
        label.setText("Device Status: OK")
    
    button = QPushButton("Check Device")
    button.clicked.connect(check_device)
    layout.addWidget(button)
    
    central.setLayout(layout)
    window.setCentralWidget(central)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    create_window()
```

**Your Assignment:**
Build a GUI for ONE task you do repeatedly:
- Component tester
- Price calculator
- Device lookup

**Start simple, add features as you learn.**

---

## 🔄 PHASE 4: AUTOMATION & SCRIPTS (Week 7-8)

### Automate Your Repetitive Tasks

**What takes you time every day?**
- Checking system status
- Organizing files
- Backing up data
- Running diagnostics

**Let's automate ONE of them.**

### Example: Auto File Organizer

```python
# organize_files.py
import os
import shutil
from pathlib import Path

def organize_downloads():
    """Sort downloads folder by file type"""
    downloads = Path.home() / "Downloads"
    
    # File type categories
    categories = {
        'Images': ['.jpg', '.png', '.gif', '.jpeg'],
        'Documents': ['.pdf', '.docx', '.txt', '.md'],
        'Code': ['.py', '.js', '.html', '.css'],
        'Archives': ['.zip', '.rar', '.7z']
    }
    
    for file in downloads.iterdir():
        if file.is_file():
            # Get file extension
            ext = file.suffix.lower()
            
            # Find category
            for category, extensions in categories.items():
                if ext in extensions:
                    # Create category folder if needed
                    category_folder = downloads / category
                    category_folder.mkdir(exist_ok=True)
                    
                    # Move file
                    shutil.move(str(file), str(category_folder / file.name))
                    print(f"Moved {file.name} to {category}")
                    break

if __name__ == "__main__":
    organize_downloads()
    print("✓ Downloads organized!")
```

**Your Assignment:**
Automate ONE thing from your daily workflow.

---

## 📊 PHASE 5: DATA & DATABASES (Week 9-10)

### Track Your Repair History

**What you need:**
- Store device info permanently
- Search past repairs
- Generate reports

**SQLite = Built-in Python Database**

```python
# repair_tracker.py
import sqlite3
from datetime import datetime

def create_database():
    """Initialize database"""
    conn = sqlite3.connect('repairs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY,
            device TEXT,
            issue TEXT,
            solution TEXT,
            cost REAL,
            date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_repair(device, issue, solution, cost):
    """Record a repair"""
    conn = sqlite3.connect('repairs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO repairs (device, issue, solution, cost, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (device, issue, solution, cost, datetime.now().strftime("%Y-%m-%d")))
    
    conn.commit()
    conn.close()
    print("✓ Repair logged")

def search_repairs(keyword):
    """Find past repairs"""
    conn = sqlite3.connect('repairs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM repairs
        WHERE device LIKE ? OR issue LIKE ?
    ''', (f'%{keyword}%', f'%{keyword}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

# Usage
create_database()
add_repair("iPhone 12", "Cracked screen", "Replaced display", 89.99)

# Search
results = search_repairs("iPhone")
for repair in results:
    print(repair)
```

**Your Assignment:**
Build a database for YOUR work. Track whatever matters to you.

---

## 🌐 PHASE 6: NETWORK & APIs (Week 11-12)

### Your Mad_SPHub Project - Understanding It

**What you've built:**
- Raspberry Pi hub
- Docker containers
- Monitoring system

**Let's understand the Python side.**

### Example: Simple HTTP Server

```python
# device_monitor.py
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

@app.route('/')
def home():
    return "Device Monitor API"

@app.route('/status')
def get_status():
    """Get system status"""
    status = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Run it, then open browser:**
`http://localhost:5000/status`

**You just built an API!**

**Your Assignment:**
Build an API that reports YOUR system info.

---

## 🎓 LEARNING RESOURCES (When You Get Stuck)

### For Your Learning Style:

**Visual/Interactive:**
- Python Tutor (pythontutor.com) - SEE code execute step-by-step
- Replit (replit.com) - Code in browser, instant results

**Hands-On:**
- Real Python (realpython.com) - Project-based tutorials
- Automate the Boring Stuff (automatetheboringstuff.com) - FREE book, practical

**Video (If helpful):**
- Corey Schafer (YouTube) - Clear Python tutorials
- Tech With Tim (YouTube) - Project-based learning

**Quick Reference:**
- Python Cheat Sheet (keep printed near workspace)
- Your own notes in Obsidian

---

## 📝 LEARNING ROUTINE (Accommodating Your Needs)

### Daily Structure:

**Morning (30-60 min):**
- Review yesterday's code
- Try ONE new thing
- Document what you learned

**Afternoon (Project Time):**
- Work on current project
- Google when stuck
- Experiment freely

**Evening (Optional):**
- Watch ONE tutorial video
- Or just review your own code

### Memory Aids:

**Document EVERYTHING in Obsidian:**
```
## Python Notes

### 2024-12-25 - Lists
- Lists use square brackets: [1, 2, 3]
- Access items: list[0] for first item
- Add items: list.append(item)
- Example I used: tools = ["screwdriver", "multimeter"]

### 2024-12-26 - Functions
- Define with `def function_name():`
- Always indent code inside function
- Return sends data back
- Example: Made device checker function
```

**Code Comments Are Your Friend:**
```python
# This checks if voltage is good
# I use this for power supply testing
# Returns True if > 5V, False otherwise
def check_voltage(volts):
    return volts > 5
```

---

## 🎯 CERTIFICATION PATH (When Ready)

### Free/Cheap Python Certifications:

**1. Python Institute PCEP (Entry Level)**
- Cost: $59
- Online exam
- Proves Python basics
- Link: pythoninstitute.org

**2. Google IT Automation with Python**
- FREE on Coursera (financial aid)
- Certificate included
- Job-relevant

**3. Microsoft Python Certification**
- Part of Azure/Microsoft Learn
- Free learning path
- Optional paid exam

**Timeline:** 3-6 months of the above learning = ready for certification

---

## ✅ HOW TO KNOW YOU'RE MAKING PROGRESS

**Week 1-2:**
✓ Can read and understand your own code
✓ Can explain what each line does

**Week 3-4:**
✓ Built at least 2 working tools
✓ Tools solve real problems for you

**Week 5-6:**
✓ Created a GUI application
✓ Application does something useful

**Week 7-8:**
✓ Automated one repetitive task
✓ Script runs without errors

**Week 9-10:**
✓ Data persists between sessions
✓ Can search/retrieve past data

**Week 11-12:**
✓ Built something network-connected
✓ Understand how your Mad_SPHub works

**After 12 weeks:**
✓ Can build tools to solve your own problems
✓ Can read and modify others' code
✓ Can explain Python concepts simply
✓ Ready to apply for junior developer roles

---

## 🚨 WHEN YOU GET FRUSTRATED

### Remember:

1. **You're not "bad at coding"** - you have a different learning style
2. **Forgetting is normal** - that's why you document everything
3. **Errors are teachers** - every error teaches you something
4. **Your pace is fine** - some learn fast, some learn deep
5. **Hardware knowledge helps** - you understand systems already

### Reset Strategies:

**Stuck on code?**
- Take 10 min break
- Explain problem out loud
- Google the exact error message
- Ask: "What's the simplest version that could work?"

**Memory issues?**
- Keep Obsidian notes open
- Comment your code heavily
- Build the same thing twice (repetition helps)
- Use your Memory.ps1 system to save sessions

**Overwhelmed?**
- Focus on ONE concept per day
- Build ONE thing per week
- Celebrate small wins
- Remember: You're learning a new language

---

## 📞 GETTING HELP

**When Asking for Help (Me or Others):**

**Bad Question:**
"My code doesn't work"

**Good Question:**
"I'm trying to save device data to a file. The file creates but stays empty. Here's my code: [paste code]. The error says: [paste error]. I've tried [what you tried]."

**Best Question:**
"Here's what I'm trying to do: [goal]. Here's my code: [code]. Here's the error: [error]. I think the problem is [your theory]. Am I on the right track?"

---

## 🎁 BONUS: Quick Wins

### 10 Python One-Liners You'll Use Constantly:

```python
# Read entire file
content = open('file.txt').read()

# Write to file
open('file.txt', 'w').write('Hello')

# List files in folder
files = os.listdir('.')

# Get current date/time
from datetime import datetime; now = datetime.now()

# Check if file exists
os.path.exists('file.txt')

# Run system command
os.system('ipconfig')

# Get file size
os.path.getsize('file.txt')

# Pause program
import time; time.sleep(5)  # 5 seconds

# Get random number
import random; num = random.randint(1, 100)

# Make HTTP request
import requests; data = requests.get('https://api.example.com').json()
```

Save these. You'll use them weekly.

---

## 🏁 FINAL THOUGHTS

**This isn't school. This is YOUR workshop.**

You're not memorizing for a test. You're building tools that make your life easier.

Every line of code you write that WORKS is a victory.
Every tool you build that you ACTUALLY USE is success.
Every problem you solve with code instead of manually is progress.

**You've got 20 years of knowing how things work.**
**Now you're learning to make things work YOUR way.**

**Let's build.**

---

*"I can do all things through Christ who strengthens me." - Philippians 4:13 (NKJV)*
# 🚀 Quick Start: GitHub Actions APK Build

## ✅ Already Done For You

1. ✅ Created `.github/workflows/build-apk.yml` - GitHub Actions workflow
2. ✅ Created `.gitignore` - Ignores build files & cache
3. ✅ Initialized Git repository locally

## 📋 Your Next 5 Steps

### **Step 1: Create GitHub Account** (if you don't have one)
- Go to https://github.com
- Click "Sign up"
- Complete registration

---

### **Step 2: Create New Repository on GitHub**

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `parking_app`
   - **Description:** "Minimalistic parking slot reservation app"
   - **Visibility:** **Public** (required for free Actions)
3. Click **"Create repository"**
4. You'll see instructions - copy the HTTPS URL

---

### **Step 3: Configure Git Locally**

Open PowerShell and run:

```powershell
cd D:\work\web_apps\parking_app

# Set your Git identity
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"

# Verify it's set
git config --global --list
```

---

### **Step 4: Push Code to GitHub**

```powershell
cd D:\work\web_apps\parking_app

# Add all files
git add .

# Commit
git commit -m "Initial commit: Parking reservation app with Flutter mobile"

# Rename branch to main (if on master)
git branch -M main

# Add GitHub remote (REPLACE with your actual GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/parking_app.git

# Push to GitHub
git push -u origin main
```

**When prompted for password:**
- Username: Your GitHub username
- Password: Use **Personal Access Token** (PAT), not password
  - Create at: https://github.com/settings/tokens
  - Scopes needed: `repo`, `workflow`

---

### **Step 5: Download Your APK**

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/parking_app`
2. Click **"Actions"** tab
3. Wait for the workflow to complete (green checkmark ✅)
4. Click on the completed workflow
5. Scroll down to **"Artifacts"**
6. Download `app-debug` or `app-release`

**Workflow takes:** 5-10 minutes total

---

## 📱 Install APK on Your Phone

### **Method 1: USB Cable (Easiest)**
```
1. Download app-debug.apk (or app-release.apk)
2. Connect phone to computer via USB
3. Copy APK to phone
4. Open file manager on phone
5. Tap app-debug.apk
6. Tap "Install"
```

### **Method 2: Email/WhatsApp**
```
1. Download APK
2. Email/WhatsApp to yourself
3. Open on phone
4. Tap to install
```

### **Method 3: QR Code**
```
1. Download APK
2. Upload to file sharing site (e.g., file.io)
3. Generate QR code
4. Scan with phone
5. Tap to install
```

---

## 🎯 Complete Workflow

```
┌─────────────────────────┐
│  You make code changes  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   git add .             │
│   git commit -m "msg"   │
│   git push              │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ GitHub Actions triggers │
│ (automatic)             │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ ⏳ Building APK...      │
│ (5-10 minutes)          │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ ✅ APK Ready!           │
│ Download from Actions   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ 📱 Install on Phone     │
│ & Test Features         │
└─────────────────────────┘
```

---

## 🔒 GitHub Personal Access Token (PAT)

If git push asks for password:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Fill:
   - **Note:** `Flutter APK Build`
   - **Expiration:** 90 days (or as preferred)
   - **Select scopes:**
     - ✅ `repo` (full control)
     - ✅ `workflow` (Actions)
4. Click **"Generate token"**
5. **Copy the token** (you won't see it again!)
6. When `git push` asks for password, paste token

---

## ✨ After First Build

**Automatic builds will happen:**
- ✅ Every time you `git push`
- ✅ APKs automatically built on GitHub's servers
- ✅ No Java 23 issues (GitHub uses Java 21)
- ✅ Download and test immediately

---

## 🧪 Test Your App

Once you install the APK on your phone:

```
✅ Login screen - Can you login?
✅ Slots screen - See parking slots?
✅ Make reservation - Can you book a slot?
✅ QR code - Does QR display?
✅ My Reservations - Can you see bookings?
✅ QR Scanner - Can you scan QR?
✅ Checkout - Can you release a slot?
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Authentication failed" | Use Personal Access Token, not password |
| "Repository not found" | Check GitHub URL is correct |
| "Workflow doesn't run" | Ensure `.github/workflows/build-apk.yml` exists |
| "No artifacts" | Check Actions tab for errors in build logs |
| "APK won't install" | Use app-debug.apk, enable unknown sources |

---

## 📊 What GitHub Actions Does

Your workflow file automatically:

1. **Checkout** your code from GitHub
2. **Install** Java 21 (no Java 23 issues!)
3. **Install** Flutter SDK
4. **Download** all dependencies
5. **Build** debug APK (~2 min)
6. **Build** release APK (~3 min)
7. **Save** both APKs as artifacts
8. **Email** you when done (optional)

---

## 🎁 Next: Advanced Setup (Optional)

Once basic builds work:

1. **Automatic testing** - Run unit tests before build
2. **Slack notifications** - Get build status on Slack
3. **Play Store release** - Auto-publish to Google Play
4. **Version tagging** - Release APKs with git tags

---

## 📞 Support

**If something goes wrong:**

1. Check GitHub Actions tab for build logs
2. Look for error messages
3. Common fixes:
   - Verify pubspec.yaml exists
   - Check `.github/workflows/build-apk.yml` path
   - Ensure main branch exists

---

## ✅ Checklist Before You Start

- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Git configured locally (`git config --global user.name/email`)
- [ ] Code pushed to GitHub (`git push`)
- [ ] Workflow visible in `.github/workflows/build-apk.yml`
- [ ] Actions tab shows running workflow
- [ ] APK downloaded from artifacts
- [ ] APK installed on phone
- [ ] App tested successfully

---

**You're ready to build!** 🚀

Just follow Steps 1-5 above and your APK will be ready in ~10 minutes!

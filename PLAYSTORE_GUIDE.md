# Complete Google Play Store Publishing Handbook for GrowthForge

This comprehensive handbook guides you step-by-step through publishing **GrowthForge** to the Google Play Store.

---

## 1. Prerequisites Checklist

- [ ] **Google Play Developer Account**: Register at [Google Play Console](https://play.google.com/console/signup) (one-time $25 USD registration fee).
- [ ] **Privacy Policy & Account Deletion URLs**: Hosted live via your deployed backend (e.g., Render, Railway, or VPS):
  - Privacy Policy: `https://<your-domain>/privacy-policy`
  - Account Deletion: `https://<your-domain>/account/delete`
- [ ] **Store Graphics Assets** (Pre-generated and ready in `store_assets/`):
  - **High-Res App Icon**: `store_assets/playstore_app_icon_512x512.png` (512x512 PNG, 32-bit color, max 1024KB).
  - **Feature Graphic**: `store_assets/playstore_feature_graphic_1024x500.png` (1024x500 PNG, no alpha).
  - **Screenshots**: At least 2 phone screenshots (take these on your mobile device or browser mobile emulator).

---

## 2. Generating Your Android App Bundle (.aab)

Google Play requires the **Android App Bundle (.aab)** format for all new apps.

### Method A: 100% Cloud Build via GitHub Actions (Recommended — Zero Local Setup)

Because local Android SDKs are large (~15-20 GB), we have already configured a complete CI/CD cloud pipeline in `.github/workflows/android-build.yml`:

1. Initialize git and push this project to your GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "feat: production GrowthForge release with Android Capacitor wrapper"
   git branch -M main
   git remote add origin https://github.com/<your-username>/growthforge.git
   git push -u origin main
   ```
2. Open your repository on GitHub and click the **Actions** tab.
3. The **"Build Android APK and Google Play Bundle (.aab)"** workflow will run automatically.
4. When finished, open the completed run and scroll to **Artifacts**:
   - `growthforge-playstore-aab`: Download this `.aab` bundle to upload to Google Play Console!
   - `growthforge-debug-apk`: Download this `.apk` to test immediately on your physical phone!

---

### Method B: Local Build (If Android Studio is Installed)

If you have Android Studio installed on your machine:
```bash
npm install
npx cap sync
npx cap open android
```
In Android Studio:
1. Go to **Build** -> **Generate Signed Bundle / APK**.
2. Select **Android App Bundle (.aab)**.
3. Follow the keystore prompt to create a keystore and compile `app-release.aab`.

---

## 3. Creating a Release Signing Keystore

To sign your `.aab` for production, generate a digital signature keystore:

```bash
keytool -genkey -v -keystore growthforge-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias growthforge
```

> [!CAUTION]
> **Backup your Keystore**: Keep `growthforge-release-key.jks` and your password in a safe, backed-up location. If lost, you cannot update your app on Google Play without resetting Play App Signing!

---

## 4. Google Play Console Step-by-Step Walkthrough

### Step 4.1: Create App
1. Log in to [Google Play Console](https://play.google.com/console).
2. Click **Create app** (top-right).
3. Fill in:
   - **App name**: `GrowthForge - Habit & Skill Tracker`
   - **Default language**: English (United States)
   - **App or game**: App
   - **Free or paid**: Free
   - Accept the Developer Program Policies and US export laws checkboxes.
4. Click **Create app**.

---

### Step 4.2: Main Store Listing Metadata

Navigate to **Grow** -> **Store presence** -> **Main store listing**:

#### Title (max 30 characters)
```
GrowthForge - Habit Tracker
```

#### Short description (max 80 characters)
```
Level up your daily habits, master new skills, and track progress with XP streaks.
```

#### Full description (max 4000 characters)
```text
Transform your ambition into reality with GrowthForge — the daily habit, task, and skill tracker engineered for high achievers.

Whether mastering a new language, leveling up your software engineering skills, or crushing daily fitness routines, GrowthForge provides the structure and gamified mechanics to forge lasting personal mastery.

⚡ CORE FEATURES:

• DAILY QUESTS & PRIORITIES:
Categorize, filter, and execute daily tasks with intuitive priority indicators. Check off completed items and earn instant XP rewards.

• DYNAMIC SKILL TREES:
Break down complex disciplines (DevOps, Strength Training, Martial Arts, Reading) into modular components and log real metrics and repetitions.

• GAMIFIED XP & STREAK TRACKING:
Maintain your daily active streak and climb from novice to Master Forger as your overall progress expands.

• WEEKLY MILESTONES:
Set weekly objectives that align daily grind with long-term vision.

• FIELD JOURNAL & SCRATCHPAD:
Record insights, workout notes, study reflections, and ideas on your synced personal memo pad.

• OFFLINE RESILIENCE & CLOUD SYNC:
Never lose momentum. Your progress is cached locally and synchronizes automatically whenever connected.

• 100% PRIVATE & SECURE:
No invasive advertising. Full user data sovereignty with instant account and data deletion support.

Forge your future today with GrowthForge.
```

#### Upload Graphics
- **App icon**: Upload `store_assets/playstore_app_icon_512x512.png`.
- **Feature graphic**: Upload `store_assets/playstore_feature_graphic_1024x500.png`.
- **Phone screenshots**: Upload at least 2 screenshots showing the Dashboard and Skill Tree tabs.

---

### Step 4.3: Mandatory Policy & Compliance Questionnaire

Navigate to **Policy** -> **App content** and complete the required declarations:

#### 1. Privacy Policy
- Paste your live Privacy Policy URL:
  `https://<your-deployed-domain>/privacy-policy`

#### 2. App Access
- Choose: *"All functionality is available without special access"* (or provide a test user credentials e.g. `testforger` / `password123` if you want reviewers to log in directly).

#### 3. Ads
- Choose: *"No, my app does not contain ads"*.

#### 4. Content Ratings
- Start questionnaire -> Category: **Utility, Productivity, Communication**.
- Violence/Sex/Drugs/Gambling: Answer **No** to all.
- User Content: Users can enter their own tasks and notes.
- Click **Save** and **Calculate rating** (usually rated Everyone / PEGI 3).

#### 5. Target Audience & Content
- Target age group: Check **18 and over** (and/or 13-17).
- Appeals to children: **No**.

#### 6. Data Safety Declaration (CRITICAL FOR APPROVAL)
Google Play strictly checks this section. Answer as follows:
- **Does your app collect or share any user data?** -> **Yes**.
- **Is all of the user data collected encrypted in transit?** -> **Yes** (HTTPS).
- **Do you provide a way for users to request that their data be deleted?** -> **Yes**!
- **Enter the deletion URL:** -> `https://<your-deployed-domain>/account/delete`.
- **Data Types Collected**:
  1. *Personal Info* -> *User IDs* (collected for Account Management & App Functionality).
  2. *Personal Info* -> *Email Address* (optional, for Account Management).
  3. *App Activity* -> *App interactions* (tasks and skill metrics created by the user).
- **Data Sharing**: *"No user data is shared with third parties"*.

---

### Step 4.4: Release the App

1. Navigate to **Release** -> **Production** (or **Testing** -> **Internal testing** for immediate verification).
2. Click **Create new release**.
3. Under **App bundles**, upload your compiled `app-release.aab`.
4. Review release notes:
   ```
   Initial production release of GrowthForge:
   - Daily task manager with priority filtering
   - Skill tree tracking with repetitions and metrics
   - XP leveling and streak flame
   - Google Play compliant account privacy controls
   ```
5. Click **Next** -> **Review release** -> **Start rollout to Production**!

Google's review team typically approves new apps within 2 to 5 business days.

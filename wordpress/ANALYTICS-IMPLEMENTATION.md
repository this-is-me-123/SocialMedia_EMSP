# WordPress Analytics Implementation Guide

This document outlines the implementation of analytics and marketing tools for the Encompass MSP WordPress website (www.encompass-msp.com).

## 1. Google Analytics 4 (GA4) Setup

### Prerequisites
- Google Analytics account with admin access
- Google Tag Manager (GTM) account
- WordPress admin access

### Implementation Steps

#### 1.1. Create GA4 Property
1. Log in to [Google Analytics](https://analytics.google.com/)
2. Click "Admin" (gear icon in the bottom left)
3. In the "Account" column, select your account or create a new one
4. In the "Property" column, click "Create Property"
5. Enter property name (e.g., "Encompass MSP")
6. Configure reporting time zone and currency
7. Click "Next" and provide business information
8. Click "Create" and accept the terms of service

#### 1.2. Set Up Data Streams
1. In your new GA4 property, go to "Data Streams"
2. Click "Add stream" and select "Web"
3. Enter website URL (https://www.encompass-msp.com)
4. Enter a stream name (e.g., "Encompass MSP Website")
5. Click "Create stream"
6. Note the Measurement ID (starts with "G-")

## 2. Google Tag Manager (GTM) Setup

### 2.1. Create GTM Account
1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Click "Create Account"
3. Enter account name (e.g., "Encompass MSP")
4. Select your country
5. Enter container name (e.g., "Encompass MSP Website")
6. Select "Web" as the target platform
7. Click "Create" and accept the terms of service

### 2.2. Install GTM on WordPress

#### Option A: Using a Plugin (Recommended)
1. In WordPress admin, go to "Plugins" > "Add New"
2. Search for "Google Site Kit by Google"
3. Click "Install Now" and then "Activate"
4. Follow the setup wizard to connect your Google account
5. In the Site Kit dashboard, click "Set up Tag Manager"
6. Select your GTM container and click "Configure Tag Manager"

#### Option B: Manual Installation
1. In GTM, click on your container ID (starts with "GTM-")
2. Copy the installation code
3. Add the code to your WordPress theme's `header.php` file just after the opening `<head>` tag
4. Add the second part of the code just after the opening `<body>` tag

## 3. Configure GA4 in GTM

### 3.1. Create GA4 Configuration Tag
1. In GTM, go to "Tags" > "New"
2. Click on "Tag Configuration"
3. Select "Google Analytics: GA4 Configuration"
4. Enter your Measurement ID (from GA4)
5. Under "Triggering", select "All Pages"
6. Name the tag "GA4 - Page View" and click "Save"

### 3.2. Set Up Enhanced Measurement
1. In GA4, go to "Admin" > "Data Streams"
2. Click on your web stream
3. Toggle on "Enhanced Measurement"
4. Configure the following events:
   - Page views
   - Scrolls (90% threshold)
   - Outbound clicks
   - Site search
   - Video engagement
   - File downloads

## 4. Implement Custom Events

### 4.1. Contact Form Submissions
1. In GTM, go to "Triggers" > "New"
2. Select "Form Submission"
3. Configure to fire on form ID or class
4. Create a new tag for the event
5. Set up the event in GA4

### 4.2. Button Clicks (e.g., "Get a Quote", "Contact Us")
1. In GTM, go to "Triggers" > "New"
2. Select "Click - Just Links" or "Click - All Elements"
3. Configure the trigger to fire on specific button IDs or classes
4. Create a new tag for the event
5. Set up the event in GA4

## 5. Verify Implementation

### 5.1. Using Google Tag Assistant
1. Install the [Google Tag Assistant](https://tagassistant.google.com/) Chrome extension
2. Navigate to your website
3. Click the Tag Assistant icon
4. Click "Enable" and refresh the page
5. Verify that GA4 and GTM tags are firing correctly

### 5.2. Using GA4 DebugView
1. In GA4, go to "Configure" > "DebugView"
2. Enable debug mode in your browser using the [GA Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna) extension
3. Interact with your website and verify events in real-time

## 6. Custom Dashboard Setup

### 6.1. Create Custom Reports
1. In GA4, go to "Reports" > "Engagement" > "Pages and screens"
2. Click "Customize report"
3. Add relevant metrics and dimensions
4. Save as a new report

### 6.2. Set Up Goals
1. In GA4, go to "Configure" > "Events"
2. Click "Create event" for each conversion goal
3. Define the event parameters that indicate a conversion
4. Mark the event as a conversion

## 7. Documentation and Handoff

### 7.1. Create User Guide
1. Document all implemented tracking
2. Create a user guide for the marketing team
3. Include instructions for accessing and interpreting reports

### 7.2. Training
1. Schedule a training session for the marketing team
2. Cover how to access reports, set up custom dashboards, and analyze data
3. Provide contact information for support

## Next Steps

1. Monitor analytics for 48 hours to ensure data is being collected correctly
2. Set up custom alerts for significant changes in traffic or conversions
3. Schedule a review meeting after 30 days to analyze initial data and make adjustments
4. Implement additional tracking as needed based on business requirements

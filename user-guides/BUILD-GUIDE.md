# C2M API Build Guide for Non-Technical Users

This guide will walk you through building the C2M API project step-by-step, whether you're working locally on your computer or using GitHub's automated system.

## Table of Contents
- [What This Project Does](#what-this-project-does)
- [Two Ways to Build](#two-ways-to-build)
- [Option 1: GitHub (Easiest)](#option-1-github-easiest)
- [Option 2: Local Build](#option-2-local-build)
- [Understanding the Output](#understanding-the-output)
- [Troubleshooting](#troubleshooting)
- [Getting Help](#getting-help)

---

## What This Project Does

The C2M API project creates documentation and testing tools for a mail processing service. Think of it like building an instruction manual that:
- Explains how to use the mail API
- Creates testing tools to verify everything works
- Publishes everything online for easy access

The build process takes source files and transforms them into:
1. **API Documentation** - Like a user manual for developers
2. **Testing Collections** - Automated tests to verify the API works
3. **Mock Servers** - Practice servers for testing without sending real mail

---

## Two Ways to Build

You have two options for building this project:

### 🌐 **Option 1: GitHub (Easiest)**
Let GitHub's servers do all the work for you. No software installation needed!

### 💻 **Option 2: Local Build**
Build on your own computer. Requires some software installation but gives you more control.

---

## Option 1: GitHub (Easiest)

### Prerequisites
- A GitHub account
- Access to the C2M API repository
- A Postman account (free at [postman.com](https://www.postman.com))

### Step-by-Step Instructions

#### 1. Get Your Postman API Key
1. Log into [Postman](https://www.postman.com)
2. Click your avatar (top right) → **Settings**
3. Click **API Keys** tab
4. Click **Generate API Key**
5. Name it "C2M API GitHub" 
6. Copy the key (starts with `PMAK-`)
7. **Save this key safely** - you'll need it next!

#### 2. Set Up GitHub Secrets
1. Go to the C2M API repository on GitHub
2. Click **Settings** tab (in the repository, not your profile)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add these secrets:
   - Name: `POSTMAN_API_KEY`
   - Value: (paste your Postman API key)
   - Click **Add secret**

#### 3. Configure Build Target
1. In the repository, find the file `.postman-target`
2. Click the pencil icon to edit
3. Make sure it contains just one word: `personal`
4. Click **Commit changes**

#### 4. Run the Build
1. Click the **Actions** tab
2. Find "Build API Spec, Collections, and Docs"
3. Click **Run workflow** button (right side)
4. Leave all options as default
5. Click the green **Run workflow** button

#### 5. Monitor Progress
1. Refresh the page after a few seconds
2. Click on the running workflow to watch progress
3. Green checkmarks = success!
4. Red X = something went wrong (see Troubleshooting)

#### 6. View Results
- **Documentation**: Check the GitHub Pages URL (usually `https://[username].github.io/c2m-api-repo`)
- **Postman**: Log into Postman and check your workspace for new collections

---

## Option 2: Local Build

### Prerequisites

You'll need to install some software first. Don't worry - we'll guide you through it!

#### For Mac Users

1. **Install Homebrew** (if not already installed):
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Required Tools**:
   ```
   brew install git node python make jq
   ```

3. **Verify Installation**:
   ```
   git --version
   node --version
   python3 --version
   make --version
   ```
   
   Each command should show a version number.

#### For Windows Users

1. **Install Git**: Download from [git-scm.com](https://git-scm.com)
2. **Install Node.js**: Download from [nodejs.org](https://nodejs.org)
3. **Install Python**: Download from [python.org](https://python.org)
4. **Install Make**: Use Git Bash (installed with Git) which includes make

### Step-by-Step Build Instructions

#### 1. Get the Code
1. Open Terminal (Mac) or Git Bash (Windows)
2. Navigate to where you want to save the project:
   ```
   cd ~/Documents
   ```
3. Clone the repository:
   ```
   git clone https://github.com/[your-org]/c2m-api-repo.git
   cd c2m-api-repo
   ```

#### 2. Set Up Environment
1. Copy the example environment file:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file with a text editor and add:
   ```
   POSTMAN_SERRAO_API_KEY=your-postman-api-key-here
   ```
   (Replace with your actual Postman API key from earlier)

#### 3. Install Dependencies
Run this command to install everything needed:
```
make install
```

This will:
- Install Node.js packages
- Set up Python environment
- Download required tools

#### 4. Run the Build
Now for the main event! Run:
```
make postman-collection-build-and-test
```

This single command will:
1. Convert data files to API specifications
2. Generate testing collections
3. Create mock servers
4. Run automated tests
5. Build documentation

#### 5. View Results
- **Documentation**: Open `http://localhost:8080` in your browser
- **Test Results**: Check the terminal output for test summaries

---

## Understanding the Output

### What Success Looks Like

When the build succeeds, you'll see:
- ✅ Green checkmarks in GitHub Actions
- ✅ "All tests passed" messages
- ✅ New collections in your Postman workspace
- ✅ Documentation available online

### What Gets Created

1. **OpenAPI Specification**
   - Technical description of the API
   - Located in `openapi/` folder

2. **Postman Collections**
   - Testing tools for the API
   - Automatically uploaded to your Postman workspace

3. **Documentation Website**
   - User-friendly API documentation
   - Published to GitHub Pages or viewable locally

4. **Mock Servers**
   - Practice servers for testing
   - No real mail is sent!

---

## Troubleshooting

### Common Issues and Solutions

#### "Command not found"
**Problem**: Missing required software
**Solution**: Go back to Prerequisites and install missing tools

#### "Permission denied"
**Problem**: No access to files or API
**Solution**: 
- Check file permissions
- Verify your Postman API key is correct
- Ensure you have repository access

#### "Postman API error"
**Problem**: Can't connect to Postman
**Solution**:
- Check your API key in `.env` file
- Ensure no extra spaces after the key
- Verify your Postman account is active

#### "Port already in use"
**Problem**: Another program is using port 4010 or 8080
**Solution**:
- Stop other development servers
- Or change ports in `.env` file

#### Build Fails in GitHub Actions
**Problem**: Red X on workflow run
**Solution**:
1. Click on the failed run
2. Click on the failed step
3. Read the error message
4. Common fixes:
   - Check API key is set correctly
   - Ensure `.postman-target` file exists
   - Verify repository settings

### Quick Fixes

#### Clean Everything and Start Fresh
```
make clean
make install
make postman-collection-build-and-test
```

#### Just Build Documentation
```
make docs
```

#### Just Run Tests
```
make test
```

---

## Getting Help

### Resources
- **Project README**: Detailed technical documentation
- **GitHub Issues**: Report problems or ask questions
- **Postman Support**: [support.postman.com](https://support.postman.com)

### Who to Contact
- **Technical Issues**: Create a GitHub issue
- **Access Problems**: Contact your team administrator
- **Postman Issues**: Use Postman's support channels

### Useful Commands for Debugging

Check what version of tools you have:
```
make version-check
```

See all available commands:
```
make help
```

Test your Postman connection:
```
make postman-test-auth
```

---

## Next Steps

Once you've successfully built the project:

1. **Explore the Documentation**: Open the generated docs and familiarize yourself with the API
2. **Try the Examples**: Use Postman to run example requests
3. **Run Tests**: Execute the test suite to ensure everything works
4. **Make Changes**: Edit the source files and rebuild to see updates

Remember: You can always rebuild the project by running the build command again. It's safe to run multiple times!

---

## Quick Reference Card

### GitHub Build
1. Set up Postman API key in GitHub Secrets
2. Ensure `.postman-target` contains "personal"
3. Go to Actions → Run workflow
4. Wait for green checkmark
5. Check Postman and GitHub Pages

### Local Build
1. Clone repository
2. Create `.env` with API key
3. Run `make install`
4. Run `make postman-collection-build-and-test`
5. View at `http://localhost:8080`

### Most Common Commands
- `make install` - Set up everything
- `make postman-collection-build-and-test` - Full build
- `make docs` - Just build documentation
- `make clean` - Remove generated files
- `make help` - Show all commands

---

**Remember**: Building software can seem complex, but this project automates most of the hard work. If you get stuck, don't hesitate to ask for help!
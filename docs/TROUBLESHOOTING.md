# Troubleshooting Guide

## Issue: "When I pick ticker, nothing happens"

### Quick Checks

1. **Check if ticker was added to watchlist**
   - Look for success message after clicking "Add"
   - Check if ticker appears in the watchlist section below

2. **Check browser console**
   - Open browser DevTools (F12)
   - Look for JavaScript errors in Console tab
   - Look for network errors in Network tab

3. **Check Streamlit logs**
   - Look at the terminal where you ran `streamlit run app.py`
   - Check for Python errors or warnings

### Common Issues

#### Issue 1: Ticker Added But No Classification Shows

**Symptoms**: Ticker appears in watchlist but no status table appears

**Possible Causes**:
- Classification is running but taking time (check for spinner)
- Error in classification (check terminal logs)
- Database connection issue

**Solution**:
1. Check terminal for errors
2. Wait a few seconds (first classification can take 5-10 seconds)
3. Refresh the page (F5)
4. Check if you see "🔍 Analyzing tickers..." spinner

#### Issue 2: Nothing Happens When Clicking "Add"

**Symptoms**: Clicking "Add" button does nothing

**Possible Causes**:
- JavaScript error in browser
- Streamlit not responding
- Button not properly connected

**Solution**:
1. Check browser console for errors
2. Try refreshing the page
3. Check if you're logged in (should see logout button in sidebar)
4. Try adding a ticker via the "Popular" buttons

#### Issue 3: App Crashes or Freezes

**Symptoms**: App becomes unresponsive or shows error

**Possible Causes**:
- API rate limiting (yfinance or RapidAPI)
- Network connectivity issues
- Memory issues

**Solution**:
1. Check terminal for error messages
2. Clear cache using "🗑️ Clear" button
3. Try again after a few minutes
4. Check internet connection

### Debug Steps

1. **Test Database**:
   ```python
   from db import SessionLocal, init_db, get_or_create_user, get_watchlist_for_user
   init_db()
   db = SessionLocal()
   user = get_or_create_user(db, 'admin')
   watchlist = get_watchlist_for_user(db, user)
   print(f"Watchlist: {watchlist}")
   ```

2. **Test Classification**:
   ```python
   from engine import classify_ticker
   result = classify_ticker('AAPL')
   print(f"Status: {result.status} {result.emoji}")
   ```

3. **Check Streamlit Version**:
   ```bash
   streamlit --version
   ```

4. **Clear Cache and Restart**:
   ```bash
   # Stop the app (Ctrl+C)
   # Clear cache
   rm -rf .streamlit/cache
   # Restart
   streamlit run app.py
   ```

### Still Not Working?

1. **Check Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Environment**:
   ```bash
   python -c "from engine import classify_ticker; print('OK')"
   ```

3. **Check Logs**:
   - Terminal output when running `streamlit run app.py`
   - Browser console (F12 → Console)
   - Streamlit logs in `.streamlit/` directory

4. **Try Minimal Test**:
   ```python
   # test_minimal.py
   import streamlit as st
   st.write("Hello World")
   ```
   Run: `streamlit run test_minimal.py`

### Getting Help

If the issue persists:
1. Check the terminal output for full error messages
2. Check browser console for JavaScript errors
3. Share the error messages for debugging


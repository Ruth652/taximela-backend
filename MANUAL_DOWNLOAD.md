# Manual OTP Download Instructions

The automatic download is failing due to network issues. Please download manually:

## Option 1: Download OTP 2.3.0 Manually

1. Open this URL in your browser:
   https://repo1.maven.org/maven2/org/opentripplanner/otp/2.3.0/otp-2.3.0-shaded.jar

2. Save the file to:
   `C:\Users\haile\Documents\taximmela\taximela-backend\otp\otp-2.3.0-shaded.jar`

3. Verify file size is around 100MB (not 21MB or 554 bytes)

4. Then run:
   ```
   .\build-graph-2.3.bat
   .\start-otp-2.3.bat
   ```

## Option 2: Use Existing OTP Installation

If you have OTP running elsewhere on your system, copy the JAR file to:
`C:\Users\haile\Documents\taximmela\taximela-backend\otp\`

## Option 3: Use wget or curl

If you have wget installed:
```bash
cd otp
wget https://repo1.maven.org/maven2/org/opentripplanner/otp/2.3.0/otp-2.3.0-shaded.jar
cd ..
```

Or with curl:
```bash
cd otp
curl -L -O https://repo1.maven.org/maven2/org/opentripplanner/otp/2.3.0/otp-2.3.0-shaded.jar
cd ..
```

## Verify Download

After downloading, check file size:
```powershell
Get-Item otp\otp-2.3.0-shaded.jar | Select-Object Name, Length
```

Should show approximately: 100,000,000 bytes (100MB)

# Fix Build Errors for ByteForgeFrontend/project/code/Tests/Integration/Performance/LoadTestingSuite.cs

## Instructions

You need to fix the following build errors in the file `ByteForgeFrontend/project/code/Tests/Integration/Performance/LoadTestingSuite.cs`. Follow these steps:

1. Read the file to understand the current code
2. Fix each error listed below
3. Run `dotnet build` to verify all errors are fixed
4. If there are still errors, fix them and build again
5. Once the build succeeds with no errors for this file, stop

## Errors to Fix

### Error 1
- **Location**: Line 72, Column 33
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'SuccessRate' and no accessible extension method 'SuccessRate' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 2
- **Location**: Line 72, Column 77
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'SuccessRate' and no accessible extension method 'SuccessRate' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 3
- **Location**: Line 73, Column 33
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'AverageResponseTime' and no accessible extension method 'AverageResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 4
- **Location**: Line 73, Column 93
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'AverageResponseTime' and no accessible extension method 'AverageResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 5
- **Location**: Line 74, Column 33
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'P95ResponseTime' and no accessible extension method 'P95ResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 6
- **Location**: Line 74, Column 86
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'P95ResponseTime' and no accessible extension method 'P95ResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 7
- **Location**: Line 72, Column 33
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'SuccessRate' and no accessible extension method 'SuccessRate' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 8
- **Location**: Line 72, Column 77
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'SuccessRate' and no accessible extension method 'SuccessRate' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 9
- **Location**: Line 73, Column 33
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'AverageResponseTime' and no accessible extension method 'AverageResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 10
- **Location**: Line 73, Column 93
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'AverageResponseTime' and no accessible extension method 'AverageResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 11
- **Location**: Line 74, Column 33
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'P95ResponseTime' and no accessible extension method 'P95ResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 12
- **Location**: Line 74, Column 86
- **Error Code**: CS1061
- **Message**: 'LoadTestingSuite.LoadTestMetrics' does not contain a definition for 'P95ResponseTime' and no accessible extension method 'P95ResponseTime' accepting a first argument of type 'LoadTestingSuite.LoadTestMetrics' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

## Important Notes

- Focus ONLY on fixing the errors listed above
- Do not make unnecessary changes to the code
- Preserve the existing functionality while fixing the errors
- Common fixes include:
  - Adding missing using statements
  - Fixing type mismatches
  - Adding null checks for nullable reference types
  - Correcting method signatures
  - Fixing namespace issues

After fixing all errors, run the build command to verify:
```bash
cd /mnt/d/Repository/@Founder-y/ByteForgeFrontend/project/code && cmd.exe /c "dotnet build"
```

Only stop when the build succeeds with no errors for this specific file.

on run argv
    set targetURL to item 1 of argv
    set jsCode to item 2 of argv
    tell application "Google Chrome"
        if it is not running then error "Google Chrome is not running"
        set foundTab to missing value
        set madeTab to false
        repeat with w in windows
            repeat with t in tabs of w
                if (URL of t) starts with targetURL then set foundTab to t
            end repeat
        end repeat
        if foundTab is missing value then
            if (count of windows) is 0 then make new window
            set foundTab to make new tab at end of tabs of front window with properties {URL:targetURL}
            set madeTab to true
        end if
        repeat 240 times
            if not (loading of foundTab) then exit repeat
            delay 0.25
        end repeat
        delay 0.4
        set theResult to (execute foundTab javascript jsCode)
        if madeTab then close foundTab
        return theResult
    end tell
end run

$token = "8627832293:AAGIjjF7V9dTKGRgTCHgM3127BF55--nz0k"
$apiUrl = "https://api.telegram.org/bot$token"
$templatePath = "C:\Users\ALTAWKEEL\.gemini\antigravity\brain\544afc12-f424-4c5d-ae90-97d62f9bdc12\scratch\welcome_payload.json"
$templateText = [System.IO.File]::ReadAllText($templatePath, [System.Text.Encoding]::UTF8)

$offset = 0
Write-Output "Telegram Bot Daemon started for @happyfarmHFCbot..."

while ($true) {
    try {
        $updatesUrl = "$apiUrl/getUpdates?offset=$offset&timeout=20"
        $res = Invoke-RestMethod -Uri $updatesUrl -Method Get -TimeoutSec 30

        if ($res.ok -and $res.result.Count -gt 0) {
            foreach ($u in $res.result) {
                $offset = $u.update_id + 1

                if ($u.message -and $u.message.text) {
                    $text = $u.message.text
                    $chatId = $u.message.chat.id
                    $user = $u.message.from
                    $fName = if ($user.first_name) { $user.first_name } else { "Farmer" }

                    if ($text.StartsWith("/start")) {
                        Write-Output "Received /start from $fName (Chat ID: $chatId)"

                        # Prepare customized JSON
                        $userPayloadText = $templateText.Replace("8745891278", "$chatId").Replace("HAPPY FARM", "$fName")
                        $bytes = [System.Text.Encoding]::UTF8.GetBytes($userPayloadText)

                        try {
                            $sendRes = Invoke-RestMethod -Uri "$apiUrl/sendMessage" -Method Post -Body $bytes -ContentType "application/json; charset=utf-8"
                            Write-Output "Welcome sent to $fName (Chat: $chatId) successfully!"
                        } catch {
                            Write-Output "Send error: $($_.Exception.Message)"
                        }
                    }
                }
            }
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

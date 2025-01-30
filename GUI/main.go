package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

type ChatRequest struct {
	Prompt string `json:"prompt"`
}

func sendMessage(input string, chatBox *widget.Label, scroll *container.Scroll) {
	url := "http://localhost:5000/chat"
	data := ChatRequest{Prompt: input}
	jsonData, _ := json.Marshal(data)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		chatBox.SetText(chatBox.Text + "\nError: Failed to create request")
		return
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		chatBox.SetText(chatBox.Text + "\nError: Failed to reach AI")
		return
	}
	defer resp.Body.Close()

	reader := io.Reader(resp.Body)
	buffer := make([]byte, 1024)
	chatBox.SetText(chatBox.Text + "\nAI: ")

	for {
		n, err := reader.Read(buffer)
		if n > 0 {
			chatBox.SetText(chatBox.Text + string(buffer[:n]))
			scroll.ScrollToBottom() // Auto-scroll when new message arrives
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			chatBox.SetText(chatBox.Text + "\nError reading response")
			break
		}
	}
}

func main() {
	myApp := app.New()
	window := myApp.NewWindow("Local AI Chat")
	window.Resize(fyne.NewSize(400, 500))

	header := widget.NewLabelWithStyle("LOCAL AI", fyne.TextAlignCenter, fyne.TextStyle{Bold: true})

	chatBox := widget.NewLabel("Welcome to Local AI Chat!")
	scroll := container.NewVScroll(chatBox)
	scroll.SetMinSize(fyne.NewSize(400, 400))

	input := widget.NewEntry()
	input.SetPlaceHolder("Type a message...")

	sendButton := widget.NewButton("Send", func() {
		if input.Text != "" {
			chatBox.SetText(chatBox.Text + "\nYou: " + input.Text)
			sendMessage(input.Text, chatBox, scroll)
			input.SetText("")
		}
	})

	input.OnSubmitted = func(text string) {
		if text != "" {
			chatBox.SetText(chatBox.Text + "\nYou: " + text)
			sendMessage(text, chatBox, scroll)
			input.SetText("")
		}
	}

	bottomContainer := container.NewBorder(nil, nil, nil, sendButton, input)

	content := container.NewBorder(header, bottomContainer, nil, nil, scroll)
	window.SetContent(content)
	window.ShowAndRun()
}

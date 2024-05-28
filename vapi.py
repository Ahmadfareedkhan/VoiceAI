from vapi_python import Vapi

# Replace 'your-public-key' with your actual Vapi public API key
vapi = Vapi(api_key='your-public-key')

# To start a call using an assistant ID
vapi.start(assistant_id='your-assistant-id')

# Or, to start a call using an assistant object configuration
assistant = {
  'firstMessage': 'Hey, how are you?',
  'context': 'You are an employee at a drive thru...',
  'model': 'gpt-3.5-turbo',
  'voice': 'jennifer-playht',
  "recordingEnabled": True,
  "interruptionsEnabled": False
}

vapi.start(assistant=assistant)


# vapi.stop()

// Create a WebSocket connection to the server using the current host and WebSocket protocol
var socket = new WebSocket("ws://" + window.location.host + "/ws");

// Get references to HTML elements
const device_a_info = document.getElementById('device_a_info');
const device_a_value = document.getElementById('device_a_value');

const device_b_info = document.getElementById('device_b_info');
const device_b_value = document.getElementById('device_b_value');

const device_c_info = document.getElementById('device_c_info');
const device_c_value = document.getElementById('device_c_value');

const send_message_info = document.getElementById('send_message_info');
const message_value = document.getElementById('message_value');
const button_send = document.getElementById('button_send');


// Handle incoming messages from the WebSocket server
socket.onmessage = function(event) {

  const data = JSON.parse(event.data);

    // Switch based on the type of attribute received
  switch(data.type){
    case 'attribute_a':
      device_a_value.textContent = data.message;
      break;
    case 'attribute_b':
      device_b_value.textContent = data.message;
      if (data.message == 'trying to connect'){
        message_value.disabled=true;
        button_send.disabled=true}
      else{
      message_value.disabled=false;
      button_send.disabled=false}
      break;
    case 'attribute_c':
      device_c_value.textContent = data.message;
      break;
  }


};

// Send a message when the button is clicked
button_send.addEventListener('click', function(){
  socket.send(message_value.value);

    // Clear the input message value
  message_value.value = '';
});


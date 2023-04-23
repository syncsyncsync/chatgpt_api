JavaScript (app.js):

const form = document.querySelector('form');
const userInput = document.querySelector('textarea[name="user_input"]');
const output = document.querySelector('#output');

form.addEventListener('submit', (event) => {
event.preventDefault();
const markdown = userInput.value;
const html = marked(markdown);
output.innerHTML = html;
});

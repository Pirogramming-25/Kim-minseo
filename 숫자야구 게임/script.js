let answer = []
let attempts = 9

const inputFields = document.querySelectorAll('.input-field')
const submitButton = document.querySelector('.submit-button')
const attemptsText = document.querySelector('#attempts')
const results = document.querySelector('#results')
const gameResultImg = document.querySelector('#game-result-img')

function createAnswer(){
    const numbers = []

    while(numbers.length < 3){
        const randomNumber = Math.floor(Math.random() * 10)

        if(!numbers.includes(randomNumber)){
            numbers.push(randomNumber)
        }
    }

    return numbers
}

function clearInputs(){
    inputFields.forEach(function(input){
        input.value = ''
    })

    inputFields[0].focus()
}

function updateAttempts(){
    attemptsText.textContent = attempts
}

function initGame(){
    answer = createAnswer()
    attempts = 9

    clearInputs()
    updateAttempts()
    results.innerHTML = ''
    gameResultImg.src = ''
    submitButton.disabled = false
}

function check_numbers(){
}

initGame()

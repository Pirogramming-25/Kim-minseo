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

function handleInputMove(){
    inputFields.forEach(function(input, index){
        input.addEventListener('input', function(){
            if(input.value !== '' && index < inputFields.length - 1){
                inputFields[index + 1].focus()
            }
        })

        input.addEventListener('keydown', function(e){
            if(e.key === 'Backspace' && input.value === '' && index > 0){
                inputFields[index - 1].focus()
            }

            if(e.key === 'Enter' && !submitButton.disabled){
                check_numbers()
            }
        })
    })
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

function getUserNumbers(){
    const userNumbers = []

    inputFields.forEach(function(input){
        userNumbers.push(input.value)
    })

    return userNumbers
}

function hasEmptyInput(userNumbers){
    return userNumbers.includes('')
}

function checkResult(userNumbers){
    let strike = 0
    let ball = 0

    userNumbers.forEach(function(number, index){
        const currentNumber = Number(number)

        if(currentNumber === answer[index]){
            strike++
        }else if(answer.includes(currentNumber)){
            ball++
        }
    })

    return {
        strike: strike,
        ball: ball
    }
}

function createResultHtml(userNumbers, result){
    const userNumberText = userNumbers.join(' ')

    if(result.strike === 0 && result.ball === 0){
        return `
            <div class="check-result" style="display: grid; grid-template-columns: 120px 20px 160px;">
                <div class="left">${userNumberText}</div>
                <div style="text-align: center;">:</div>
                <div class="right" style="text-align: center;"><span class="num-result out">O</span></div>
            </div>
        `
    }

    return `
        <div class="check-result" style="display: grid; grid-template-columns: 120px 20px 160px;">
            <div class="left">${userNumberText}</div>
            <div style="text-align: center;">:</div>
            <div class="right" style="text-align: center;">
                ${result.strike} <span class="num-result strike">S</span>
                ${result.ball} <span class="num-result ball">B</span>
            </div>
        </div>
    `
}

function addResult(userNumbers, result){
    results.insertAdjacentHTML('beforeend', createResultHtml(userNumbers, result))
}

function finishGame(imageName){
    gameResultImg.src = imageName
    submitButton.disabled = true
}

function check_numbers(){
    const userNumbers = getUserNumbers()

    if(hasEmptyInput(userNumbers)){
        clearInputs()
        return
    }

    attempts--
    updateAttempts()

    const result = checkResult(userNumbers)

    addResult(userNumbers, result)
    clearInputs()

    if(result.strike === 3){
        finishGame('success.png')
        return
    }

    if(attempts === 0){
        finishGame('fail.png')
    }
}

initGame()
handleInputMove()

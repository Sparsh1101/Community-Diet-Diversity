function addSpace(element) {
    let ele = document.getElementById(element.id)
    ele = ele.value.split(' ').join('')
    let finalVal = ele.match(/.{1,4}/g).join(' ')
    document.getElementById(element.id).value = finalVal
}
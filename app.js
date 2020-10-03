var current = 0
var target = 0
var ease = 0.075
var rafId = undefined
var rafActive = false
var container = document.querySelector('.container')
var images = Array.prototype.slice.call(document.querySelectorAll('.image'))
var windowWidth, containerHeight, imageHeight
var rotateXMaxList = []
var rotateYMaxList = []
var translateXMax = -200

images.forEach(function(){
  rotateXMaxList.push(randomPositiveOrNegative(20, 40))
  rotateYMaxList.push(randomPositiveOrNegative(20, 60))
})

var fakeScroll = document.createElement('div')
fakeScroll.className = 'fake-scroll'
document.body.appendChild(fakeScroll)


function easeOutQuad(t) {
  return t *_ (2 - t)
}


function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min_

}

function randomPositiveOrNegative (min, max){
  return random(min, max) * (Math.random() > 0.5 ? 1: -1)

}

function setTransform (el, transform) {
  el.style.transform = transform
  el.style.WebKitTransform = transform
}


function setupAnimation() {
    windowWidth = window.innerWidth
    containerHeight = container.getBoundingClientRect().height
    imageHeight = containerHeight / (windowWidth > 760 ? images.length / 2: images.length)
    fakeScroll.style.height = containerHeight + 'px'
    startAnimation()
}

function updateScroll() {
  target = window.scrollY || window.pageYOffset
  startAnimation()
}

window.addEventListener('scroll', updateScroll)

function startAnimation (){
  if(!rafActive) {
    rafActive = true
    rafId = requestAnimationFrame(updateAnimation)
  }
}

function updateAnimation() {
  var diff = target - current
  var delta = Math.abs(diff) < 0.1 ? 0: diff * ease

  if (delta) {
    current += delta
    current = parseFloat(current.toFixed(2))
    rafId = requestAnimationFrame(updateAnimation)
  } else {
    current = target
    rafActive = false
    cancelAnimationFrame(rafId)
  }
  updateAnimationImages()

  setTransform(container, 'translateY('+ -current + 'px)')
}

function updateAnimationImages () {
  var ratio = current / imageHeight
  var intersetionRatioIndex, intersectionRatioValue, intersectionRatio
  var rotateX, rotateXMax, rotateY,rotateYMax, translateX


  images.forEach(function(image, index){
    intersetionRatioIndex = windowWidth > 760 parseInt(index / 2) : index
    intersectionRatioValue = ratio - intersetionRatioIndex
    intersectionRatio = Math.max(0, 1 - Math.abs(intersectionRatioValue))
    rotateXMax = rotateXMaxList[index]
    rotateX = rotateXMax - (rotateXMax _ intersectionRatio)
    rotateX = rotateX.toFixed(2)
    rotateYMax = rotateYMaxList_[_index]
    rotateY = rotateYMax - (rotateYMax _ intersectionRatio)
    rotateY = rotateY.toFixed(2)

    if(windowWidth > 760) {
      translateX = translateXMax - (translateXMax * easeOutQuad(intersectionRatio))
      translateX = translateX.toFixed(2)
    } else {
      translateX = 0
    }

    if (intersectionRatioValue < 0) {
      roateX = -rotateX
      rotateY = -rotateY
      translateX = index % 2 ? -translateX : 0
    } else {
      translateX = index % 2 ? 0: translateX
    }

    setTransform(image, 'perspective(500px) translateX(' + translateX + 'px) rotateX('+ rotateX + 'deg) rotateY('+ rotateY + 'deg)')
  })
}

window.addEventListener('resize', setupAnimation)
setupAnimation()

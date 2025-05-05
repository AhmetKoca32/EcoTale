document.addEventListener("DOMContentLoaded", function () {
	// Elements
	const carousel = document.getElementById("memory-carousel");
	const cards = document.querySelectorAll(".memory-card");
	const prevBtn = document.getElementById("prev-btn");
	const nextBtn = document.getElementById("next-btn");

	// Variables
	let currentIndex = 0;
	let startX, startY;
	let isDragging = false;
	let isAnimating = false;
	const totalCards = cards.length;
	const transitionDuration = 500; // milliseconds

	// Initialize
	function init() {
		// Position cards
		updateCardPositions();

		// Add event listeners
		prevBtn.addEventListener("click", handlePrevClick);
		nextBtn.addEventListener("click", handleNextClick);
		cards.forEach((card) => {
			card.addEventListener("click", flipCard);
		});

		// Touch/mouse events for dragging
		carousel.addEventListener("mousedown", dragStart);
		carousel.addEventListener("touchstart", dragStart, { passive: true });
		document.addEventListener("mousemove", drag);
		document.addEventListener("touchmove", drag, { passive: false });
		document.addEventListener("mouseup", dragEnd);
		document.addEventListener("touchend", dragEnd);

		// Keyboard navigation
		document.addEventListener("keydown", handleKeyDown);
	}

	// Update card positions and visibility
	function updateCardPositions() {
		cards.forEach((card, index) => {
			// Remove all classes first
			card.classList.remove('active', 'prev', 'next', 'prev-2', 'next-2', 'prev-3', 'next-3', 'far-prev', 'far-next');
			
			// Calculate relative position
			let relativeIndex = (index - currentIndex + totalCards) % totalCards;
			
			// Add appropriate class based on position
			if (relativeIndex === 0) {
				card.classList.add('active');
			} else if (relativeIndex === 1) {
				card.classList.add('next');
			} else if (relativeIndex === totalCards - 1) {
				card.classList.add('prev');
			} else if (relativeIndex === 2) {
				card.classList.add('next-2');
			} else if (relativeIndex === totalCards - 2) {
				card.classList.add('prev-2');
			} else if (relativeIndex === 3) {
				card.classList.add('next-3');
			} else if (relativeIndex === totalCards - 3) {
				card.classList.add('prev-3');
			} else if (relativeIndex < totalCards - 3) {
				card.classList.add('far-prev');
			} else {
				card.classList.add('far-next');
			}
		});
	}

	// Handle previous button click
	function handlePrevClick() {
		if (!isAnimating) {
			isAnimating = true;
			prevCard();
			setTimeout(() => {
				isAnimating = false;
			}, transitionDuration);
		}
	}

	// Handle next button click
	function handleNextClick() {
		if (!isAnimating) {
			isAnimating = true;
			nextCard();
			setTimeout(() => {
				isAnimating = false;
			}, transitionDuration);
		}
	}

	// Next card
	function nextCard() {
		currentIndex = (currentIndex + 1) % totalCards;
		updateCardPositions();
	}

	// Previous card
	function prevCard() {
		currentIndex = (currentIndex - 1 + totalCards) % totalCards;
		updateCardPositions();
	}

	// Flip card and toggle selection
	function flipCard(e) {
		const card = e.currentTarget;

		// Remove 'selected' class from all cards
		document.querySelectorAll('.memory-card').forEach(c => c.classList.remove('selected'));

		// Add 'selected' class to the clicked card
		card.classList.add('selected');

		// Flip the card if it's the active one
		if (card.classList.contains('active')) {
			card.classList.toggle("flipped");
		}

		// Sağ alttaki butonu göster
		const button = document.getElementById('loading-button');
		button.style.display = 'block';
	}

	// Butona tıklandığında loading animasyonunu başlat ve sayfayı değiştir
	document.getElementById('loading-button').addEventListener('click', function() {
		const loadingAnimation = document.querySelector('.loading');
		loadingAnimation.style.display = 'block'; // Loading animasyonunu göster
		
		// 10 saniye sonra yönlendirme yap (loading animasyonu ile aynı süre)
		setTimeout(function() {
			window.location.href = 'story'; // Yeni sayfaya yönlendir
		}, 10000); // 10 saniye sonra yönlendir
	});

	// Card'lar üzerinde tıklama olayını dinle
	document.querySelectorAll('.memory-card').forEach(card => {
		card.addEventListener('click', flipCard);
	});




	// Drag functions
	function dragStart(e) {
		if (isAnimating) return;
		e.preventDefault();
		isDragging = true;
		startX = e.pageX || e.touches[0].pageX;
	}

	function drag(e) {
		if (!isDragging || isAnimating) return;
		e.preventDefault();

		const currentX = e.pageX || (e.touches ? e.touches[0].pageX : startX);
		const diffX = currentX - startX;

		// Calculate drag threshold
		const threshold = window.innerWidth * 0.2; // 20% of screen width

		if (Math.abs(diffX) > threshold) {
			if (diffX > 0) {
				handlePrevClick();
			} else {
				handleNextClick();
			}
			isDragging = false;
		}
	}

	function dragEnd(e) {
		if (!isDragging || isAnimating) return;
		isDragging = false;

		const currentX = e.pageX || (e.changedTouches ? e.changedTouches[0].pageX : startX);
		const diffX = currentX - startX;

		// If drag distance is significant, change card
		if (Math.abs(diffX) > 50) {
			if (diffX > 0) {
				handlePrevClick();
			} else {
				handleNextClick();
			}
		}
	}

	// Keyboard navigation
	function handleKeyDown(e) {
		if (isAnimating) return;
		
		if (e.key === "ArrowLeft") {
			handlePrevClick();
		} else if (e.key === "ArrowRight") {
			handleNextClick();
		} else if (e.key === "Enter" || e.key === " ") {
			const currentCard = cards[currentIndex];
			if (currentCard) {
				currentCard.classList.toggle("flipped");
			}
		}
	}

	// Initialize the carousel
	init();
});

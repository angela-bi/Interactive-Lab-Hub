function setup() {
	createCanvas(400, 200);
  }
  
  function draw() {
	background(220);
	
	let hr = hour();
	let mn = minute();
	let sc = second();
	let date = new Date();
	let ms = date.getMilliseconds();
	
	push();
	// noFill();
	fill(0,50)
	noStroke()
	translate(200, 100);
	for (let i = 0; i < 10; i++) {
	  ellipse(hr, mn, ms, hr);
	  rotate(PI / max(1, sc));
	}
	pop();
	let formattedHr = nf(hr, 2);
	let formattedMn = nf(mn, 2);
	let formattedSc = nf(sc, 2);
  
	let timeString = formattedHr + ":" + formattedMn + ":" + formattedSc;
	
  
	push();
	  drawingContext.save();
	drawingContext.globalCompositeOperation = 'difference';
	fill(255);
	textSize(60);
	textAlign(CENTER, CENTER);
	text(timeString, width / 2, height / 2); // Display time in the center
	pop();
	
	blendMode(BLEND);
  }
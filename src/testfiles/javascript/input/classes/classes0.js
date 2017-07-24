// Examples captured from "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes"

class Rectangle {
  constructor(height, width) {
    this.height = height;
    this.width = width;
  }
  
  get area() {
    return this.calcArea();
  }

  calcArea() {
    return this.height * this.width;
  }
}

const square = new Rectangle(10, 10);

class Point {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }

  static distance(a, b) {
    const dx = a.x - b.x;
    const dy = a.y - b.y;

    return Math.sqrt(dx*dx + dy*dy);
  }
}

const p1 = new Point(5, 5);
const p2 = new Point(10, 10);

console.log(Point.distance(p1, p2));

class MyArray extends Array {
  // Overwrite species to the parent Array constructor
  static get [Symbol.species]() { return Array; }
}

var a = new MyArray(1,2,3);
var mapped = a.map(x => x * x);

const el = (id) => document.getElementById(id);

const container = el("scrollContainer");
const leftButton = el("leftButton");
const rightButton = el("rightButton");

const updateButtonState = () => {
  const isOverflowing = container.scrollWidth > container.clientWidth;

  container.style.justifyContent = isOverflowing ? "normal" : "center";
  leftButton.style.display = isOverflowing ? "block" : "none";
  rightButton.style.display = isOverflowing ? "block" : "none";

  if (isOverflowing) {
    leftButton.disabled = container.scrollLeft <= 0;
    rightButton.disabled =
      container.scrollLeft >= container.scrollWidth - container.clientWidth - 1;
  }
};

const scrollSlide = (direction) =>
  container.scrollBy({
    left: container.clientWidth * direction,
    behavior: "smooth",
  });

container.addEventListener("scroll", updateButtonState);
window.addEventListener("resize", updateButtonState);
window.addEventListener("load", updateButtonState);

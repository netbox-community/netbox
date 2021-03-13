import Choices from "choices.js";

export function initStaticSelect() {
  const elements = document.querySelectorAll(
    ".netbox-select2-static"
  ) as NodeListOf<HTMLSelectElement>;

  for (const element of elements) {
    if (element !== null) {
      new Choices(element, {
        noChoicesText: "No Options Available",
        itemSelectText: "",
      });
    }
  }
}

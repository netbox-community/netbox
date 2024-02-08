export const config = {
  plugins: {
    // Provides the "clear" button on the widget
    clear_button: {
      html: (data: Dict) =>
        `<i class="mdi mdi-close-circle ${data.className}" title="${data.title}"></i>`,
    },
  },
};

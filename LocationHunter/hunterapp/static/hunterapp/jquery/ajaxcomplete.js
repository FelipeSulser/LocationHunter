$(function() {
    availableSports = ["Basketball","Football","Baseball"];
  $("#sport").autocomplete({
      source: availableSports
  });
});
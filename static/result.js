// [specific] result screen element
const fixResultButtons = document.querySelectorAll(".fix-result-button");

const SCROLL_STORAGE_KEY = "resultScrollY";

fixResultButtons.forEach((button) => {
  button.addEventListener("click", async () => {

    const startId = button.dataset.startId;
    const rowNumber = button.dataset.rowNumber;

    const formData = new FormData();
    formData.append("startId", startId);
    formData.append("rowNumber", rowNumber);

    document.body.setAttribute('inert', 'true');

    try {
      await fetch("/fix_result", {
        method: "POST",
        body: formData
      });

      sessionStorage.setItem(SCROLL_STORAGE_KEY, window.scrollY);
      location.reload();
    } catch (error) {
      alert("通信エラーが発生しました。");
      document.body.removeAttribute('inert');
    }
  });
});

const storedScrollY = sessionStorage.getItem(SCROLL_STORAGE_KEY);
if (storedScrollY !== null) {
  sessionStorage.removeItem(SCROLL_STORAGE_KEY);
  window.scrollTo(0, parseInt(storedScrollY, 10));
}

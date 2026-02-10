const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();
tg.setBackgroundColor("#0b0618");
tg.setHeaderColor("#0b0618");

function activate() {
  tg.HapticFeedback.impactOccurred("medium");

  tg.showPopup({
    title: "Premium Access",
    message: "Subscription / AI / SaaS logic goes here",
    buttons: [
      { id: "ok", type: "ok", text: "Continue" }
    ]
  });
}


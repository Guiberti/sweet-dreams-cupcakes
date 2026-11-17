// Sweet Dreams - interações do front-end (JavaScript puro, sem dependências).
// Tudo aqui é melhoria progressiva: o app funciona mesmo sem JavaScript.
(function () {
  const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));

  // Fechar alertas
  $$(".alerta .fechar").forEach((b) => b.addEventListener("click", () => b.parentElement.remove()));

  // Seletor de quantidade (+ / −)
  $$(".qtd").forEach((box) => {
    const input = box.querySelector("input");
    const max = parseInt(box.dataset.max || "99", 10);
    const min = parseInt(input.min || "1", 10);
    const auto = box.hasAttribute("data-auto-submit");
    const mudar = (delta) => {
      const v = Math.min(max, Math.max(min, (parseInt(input.value, 10) || 0) + delta));
      input.value = v;
      if (auto) box.closest("form").submit();
    };
    box.querySelector(".qtd-menos").addEventListener("click", () => mudar(-1));
    box.querySelector(".qtd-mais").addEventListener("click", () => mudar(1));
    if (auto) input.addEventListener("change", () => box.closest("form").submit());
  });

  // Recalcular frete ao trocar tipo de entrega/endereço
  $$("[data-auto-submit-change]").forEach((el) => el.addEventListener("change", () => el.form.submit()));

  // Confirmação antes de ações destrutivas
  $$("form[data-confirmar]").forEach((f) =>
    f.addEventListener("submit", (e) => { if (!confirm(f.dataset.confirmar)) e.preventDefault(); }));

  // Mostrar/ocultar senha
  $$(".ver-senha").forEach((b) => b.addEventListener("click", () => {
    const i = document.getElementById(b.dataset.alvo);
    i.type = i.type === "password" ? "text" : "password";
    b.setAttribute("aria-label", i.type === "password" ? "Mostrar senha" : "Ocultar senha");
  }));

  // Abas de pagamento (Cartão / PIX)
  $$(".aba").forEach((aba) => aba.addEventListener("click", () => {
    $$(".aba").forEach((a) => { a.classList.remove("ativa"); a.setAttribute("aria-selected", "false"); });
    $$(".painel-aba").forEach((p) => (p.hidden = true));
    aba.classList.add("ativa"); aba.setAttribute("aria-selected", "true");
    document.getElementById(aba.dataset.aba).hidden = false;
  }));

  // Copiar código PIX
  $$("[data-copiar]").forEach((b) => b.addEventListener("click", async () => {
    const campo = document.getElementById(b.dataset.copiar);
    try { await navigator.clipboard.writeText(campo.value); } catch (_) { campo.select(); document.execCommand("copy"); }
    b.textContent = "Código copiado ✓";
  }));

  // Máscaras de entrada
  const mascaras = {
    telefone: (v) => v.replace(/\D/g, "").slice(0, 11).replace(/^(\d{2})(\d)/, "($1) $2").replace(/(\d)(\d{4})$/, "$1-$2"),
    cep: (v) => v.replace(/\D/g, "").slice(0, 8).replace(/^(\d{5})(\d)/, "$1-$2"),
    cartao: (v) => v.replace(/\D/g, "").slice(0, 19).replace(/(\d{4})(?=\d)/g, "$1 "),
    validade: (v) => v.replace(/\D/g, "").slice(0, 4).replace(/^(\d{2})(\d)/, "$1/$2"),
  };
  $$("[data-mascara]").forEach((i) => i.addEventListener("input", () => { i.value = mascaras[i.dataset.mascara](i.value); }));
})();

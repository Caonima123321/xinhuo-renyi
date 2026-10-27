import io, os, re
root = r"C:\Users\春生\Desktop\农创"
src = open(os.path.join(root, "薪火仁义-交互原型.html"), encoding="utf-8").read()

test_js = """
<script>
(function(){
  const log = [];
  const ok = (name, cond) => log.push((cond ? 'PASS ' : 'FAIL ') + name);
  function active(){ const s=document.querySelector('.screen.active'); return s ? s.dataset.screen : null; }
  window.addEventListener('load', () => {
    setTimeout(() => {
      go('course'); ok('nav course', active()==='course');
      go('book'); ok('nav book', active()==='book');
      stepPeople(5); const pn=document.getElementById('peopleNum').textContent;
      ok('people 45', pn==='45');
      const total=document.getElementById('totalPrice2').textContent;
      ok('total recalc', total.indexOf('7,020')>=0 || total.indexOf('7,0')>=0);
      toggleAdd(document.querySelector('[data-add=photo]'));
      ok('addon toggle', state.addons.photo===true);
      go('schedule'); go('confirm'); openPay();
      ok('pay sheet open', document.getElementById('sheetPay').classList.contains('on'));
      paySuccess();
      setTimeout(() => {
        ok('pay -> success', active()==='success');
        go('poi'); checkin();
        setTimeout(() => {
          ok('stamps 8', state.stamps===8);
          const btn=document.getElementById('certBtn').textContent;
          ok('cert unlocked', btn.indexOf('证书')>=0);
          go('cert'); ok('nav cert', active()==='cert');
          go('vendor'); doVerify();
          setTimeout(() => {
            ok('verify -> vendor', active()==='vendor');
            const fails = log.filter(x=>x.startsWith('FAIL'));
            const d=document.createElement('div');
            d.style.cssText='position:fixed;left:0;right:0;top:0;z-index:99999;background:'+(fails.length?'#c00':'#0a7')+';color:#fff;font:11px/1.5 monospace;padding:6px;white-space:pre-wrap';
            d.textContent = log.join('  |  ') + (fails.length? '  <<< HAS FAILURES' : '  <<< ALL PASS');
            document.documentElement.appendChild(d);
          }, 1200);
        }, 2600);
      }, 700);
    }, 400);
  });
})();
</script>
"""
out = src.replace("</body>", test_js + "</body>")
p = os.path.join(os.environ["TEMP"], "test_flow.html")
open(p, "w", encoding="utf-8").write(out)
print("written", p)

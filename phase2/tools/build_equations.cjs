const fs=require('fs'), path=require('path');
const req=require('module').createRequire(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'anchor.js'));
const sharp=req('sharp');const mathreq=process.env.HEMCGA_DOC_NODE_MODULES ? require('module').createRequire(path.join(process.env.HEMCGA_DOC_NODE_MODULES,'anchor.js')) : req;
const {mathjax}=mathreq('mathjax-full/js/mathjax.js');const {TeX}=mathreq('mathjax-full/js/input/tex.js');
const {SVG}=mathreq('mathjax-full/js/output/svg.js');const {liteAdaptor}=mathreq('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=mathreq('mathjax-full/js/handlers/html.js');const {AllPackages}=mathreq('mathjax-full/js/input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'local'})});
const equations={
 fractions:String.raw`w_i=\frac{x_iM_i}{\sum_jx_jM_j},\quad v_i=\frac{x_iM_i/\rho_i}{\sum_jx_jM_j/\rho_j},\quad\rho=\frac{\sum_i x_iM_i}{\sum_i x_iM_i/\rho_i}`,
 entropy:String.raw`\Delta S_{\mathrm{ideal}}=-R\sum_i x_i\ln x_i,\qquad G=H-TS`,
 objective:String.raw`J=\frac{\sigma_{\max}}{1000}+0.2\frac{\rho}{10}-0.2\frac{L_c}{1000}+0.25D+0.5F+0.1\frac{m_A}{20}`,
 conduction:String.raw`R_A=\sum_j\frac{d_j}{k_j},\qquad q=\frac{T_h-T_c}{R_A},\qquad T_{j+1}-T_j=q\frac{d_j}{k_j}`,
 stress:String.raw`\sigma(z)=\frac{E(z)}{1-\nu(z)}\left[\epsilon_0+\kappa\left(z-\frac{L}{2}\right)-\alpha(z)\left(T(z)-T_0\right)\right]`,
 gradient:String.raw`f_c(z)=\left(\frac{z}{L}\right)^n,\quad\overline f_{c,j}=\frac{(z_{j+1}/L)^{n+1}-(z_j/L)^{n+1}}{(n+1)(z_{j+1}-z_j)/L},\quad\overline f_c=\frac{1}{n+1}`
};
(async()=>{let out=path.join(__dirname,'../assets');fs.mkdirSync(out,{recursive:true});for(let [name,tex] of Object.entries(equations)){
 let html=adaptor.outerHTML(doc.convert(tex,{display:true}));let svg=html.slice(html.indexOf('<svg'),html.indexOf('</svg>')+6);
 if(!svg.includes('xmlns='))svg=svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ');
 svg=svg.replace(/(width|height)="([0-9.]+)(ex|em)"/g,(_,a,b)=>`${a}="${Math.round(Number(b)*9)}px"`).replace(/currentColor/g,'#000000');
 await sharp(Buffer.from(svg),{density:400}).png().toFile(path.join(out,name+'.png'));
}})().catch(e=>{console.error(e);process.exit(1)});

define <4 x float> @vector_add(<4 x float> %a, <4 x float> %b) {
  %res = fadd <4 x float> %a, %b
  ret <4 x float> %res
}

define <4 x float> @vector_relu(<4 x float> %a) {
  %zero = fcmp ogt <4 x float> %a, zeroinitializer
  %res = select <4 x i1> %zero, <4 x float> %a, <4 x float> zeroinitializer
  ret <4 x float> %res
}

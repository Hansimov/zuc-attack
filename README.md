## 相关系数公式及其变形

总体相关系数：
$$
\rho _{X,Y} = \frac{cov(X,Y)}{\sigma_X \cdot \sigma_Y}
$$

样本相关系数：
$$
\begin{align}
r & = \frac{\sum_{i=1}^{n}(X_i-\overline{X})(Y_i-\overline{Y})}{\sqrt{\sum_{i=1}^n(X_i-\overline{X})^2}\sqrt{\sum_{i=1}^n(Y_i-\overline{Y})^2}} 
\end{align}
$$
对分式各部分进行数学变换：

（1）分子：
$$
\begin{align}
\sum_{i=1}^{n}(X_i-\overline{X})(Y_i-\overline{Y}) & =\sum_{i=1}^{n}(X_i Y_i + \overline{X}\overline{Y}-X_i\overline{Y}-\overline{X}Y_i) \\
& = \sum_{i=1}^{n}X_i Y_i + \sum_{i=1}^{n}\overline{X}\overline{Y}-\sum_{i=1}^{n}X_i\overline{Y}-\sum_{i=1}^{n}\overline{X}Y_i \\
& =  \sum_{i=1}^{n}X_i Y_i + n \overline{X}\overline{Y} -  (n \overline{X})\overline{Y} - (n \overline{Y})\overline{X} \\
& = \sum_{i=1}^{n}X_i Y_i - n \overline{X}\overline{Y}
 \end{align}
$$
（2）分母：
$$
\begin{align}
\sum_{i=1}^n(X_i-\overline{X})^2 & = \sum_{i=1}^n(X_i^2+\overline{X}^2-2 X_i \overline{X}) \\
& = \sum_{i=1}^n X_i^2 + \sum_{i=1}^n \overline{X}^2-2 \sum_{i=1}^n X_i \overline{X} \\
& = \sum_{i=1}^n X_i^2 + n \overline{X}^2 - 2 n \overline{X} \cdot \overline{X} \\
& = \sum_{i=1}^n X_i^2 - n \overline{X}^2 \\
\sum_{i=1}^n(Y_i-\overline{Y})^2  &= \sum_{i=1}^n Y_i^2 - n \overline{Y}^2
\end{align}
$$
得：
$$
\begin{align}
r & = \frac{\sum_{i=1}^{n}(X_i-\overline{X})(Y_i-\overline{Y})}{\sqrt{\sum_{i=1}^n(X_i-\overline{X})^2}\sqrt{\sum_{i=1}^n(Y_i-\overline{Y})^2}} \\
& = \frac{\sum_{i=1}^{n}X_i Y_i - n \overline{X}\overline{Y}}{\sqrt{\sum_{i=1}^n X_i^2 - n \overline{X}^2}\sqrt{\sum_{i=1}^n Y_i^2 - n \overline{Y}^2}}
\end{align}
$$
亦即：
$$
r_n = f((X1,Y1),(X_2,Y2),...(X_n,Y_n))
$$
其中 n 为样本点数，在功耗分析中，为曲线条数。

<hr>

变形后的公式使样本点彼此独立，这样可以记录历史运算结果，还能够并行化，极大地提高了计算效率。

各部分的递推公式如下：

（1）求和公式：
$$
\begin{align}
\sum_{i=1}^{n+k}X_iY_i & = \sum_{i=1}^n{X_iY_i}+\sum_{i=n+1}^{n+k}{X_iY_i} \\
\sum_{i=1}^{n+k}X_i^2 & = \sum_{i=1}^n{X_i^2}+\sum_{i=n+1}^{n+k}{X_i^2} \\
\sum_{i=1}^{n+k}Y_i^2 & = \sum_{i=1}^n{Y_i^2}+\sum_{i=n+1}^{n+k}{Y_i^2} \\

\end{align}
$$
（2）求均公式：
$$
\begin{align}
\overline{X}_{n+k} & = \frac{1}{n+k}\sum_{i=1}^{n+k} X_i  \\
 & = \frac{1}{n+k}(\sum_{i=1}^{n}X_i+\sum_{i=n+1}^{n+k}X_i) \\
 \end{align}
$$



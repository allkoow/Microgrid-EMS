load res.txt

subplot(2,1,1);
hold on
stairs(1:24,res(:,1));
stairs(1:24,res(:,4));
hold off
title('zasoby w³asne');
legend('P_{RES,U}','P_{ES,U}');
xlabel('czas [h]');
ylabel('moc [kW]');
xlim([1 24]);
grid;

subplot(2,1,2);
hold on
stairs(1:24,res(:,6));
stairs(1:24,res(:,8));
hold off
title('zasoby innych u¿ytkowników');
legend('M_U','G_U');
xlabel('czas [h]');
ylabel('moc [kW]');
xlim([1 24]);
grid;
function create_plot(a,b,filename)


x = a:b;
y = x.^2;



fig = figure('Visible','off'); % Prevents automatically showing the figure
plot(x,y,'Linewidth',2);
title('Graph');
grid on;


% Force .jpg output
    [folder, name, ~] = fileparts(filename);
    jpgFile = fullfile(folder, [name '.jpg']);
    saveas(fig, jpgFile, 'jpg');

    close(fig);

end


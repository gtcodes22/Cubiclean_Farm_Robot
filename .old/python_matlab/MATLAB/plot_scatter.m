function plot_scatter(x, y, filename)
    scatter(x, y, 'filled') % scatter function using x y co-ordinates passed from Python
    xlabel('X Position')
    ylabel('Y Position')
    title('Odometry Samples')
    grid on
    saveas(gcf, filename) % save figure as JPEG
end

document.addEventListener('DOMContentLoaded', function() {
    const moviesList = document.getElementById('movie-list');
    const singleMovieDetails = document.getElementById('single-movie-details');
    const hideMoviesButton = document.getElementById('hide-movies');
    const updateMovieButton = document.getElementById('update-movie-button');
    const updateMovieSection = document.getElementById('update-movie-section');
    const viewSingleMovieForm = document.getElementById('view-single-movie-form');
    const updateMovieForm = document.getElementById('update-movie-form');
    const addMovieForm = document.getElementById('add-movie-form');
    const clearUpdateFormButton = document.getElementById('clear-update-form');
    const clearAddFormButton = document.getElementById('clear-add-form');
    const revenueBudgetChartElement = document.getElementById('revenue-budget-chart').getContext('2d');
    const highestGrossingMovieButton = document.getElementById('highest-grossing-movie');
    const highestGrossingMovieDetails = document.getElementById('highest-grossing-movie-details');
    const viewMovieAnalyticsButton = document.getElementById('view-movie-analytics');
    const analyticsSection = document.querySelector('.analytics-section');
    let revenueBudgetChart;

    let chartInitialized = false;

    function fetchMovies() {
        console.log('Fetching movies from server...');
        fetch('/movies')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok: ' + response.statusText);
                return response.json();
            })
            .then(data => {
                console.log('Movies fetched:', data);
                moviesList.innerHTML = ''; // Clear the existing content
                data.forEach(movie => {
                    const div = document.createElement('div');
                    div.innerHTML = `ID: ${movie.id} - Title: ${movie.title}`;
                    moviesList.appendChild(div);
                });
                moviesList.style.display = 'block'; // Make the movie list visible
                hideMoviesButton.style.display = 'inline'; // Show the Hide Movies button

                // Update the analytics chart
                if (data.length > 0) {
                    setTimeout(() => {
                        if (revenueBudgetChartElement.canvas) { // Ensure the canvas context is available
                            updateAnalyticsChart(data);
                        } else {
                            console.error('Canvas context is not available.');
                        }
                    }, 500); // Delay initialization to ensure the DOM is fully loaded
                }
            })
            .catch(error => {
                console.error('Error fetching movies:', error);
            });
    }

    function fetchSingleMovie(event) {
        event.preventDefault();
        const movieId = new FormData(event.target).get('id');
        fetch(`/movies/${movieId}`)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok: ' + response.statusText);
                return response.json();
            })
            .then(movie => {
                const releaseDate = new Date(movie.release_date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });

                singleMovieDetails.innerHTML = `
                    <div class="movie-details">
                        <div class="text">
                            <h2>${movie.title}</h2>
                            <p>Release Date: ${releaseDate}</p>
                            <p>Rating: ${movie.rating}</p>
                            <p>Votes: ${movie.vote_count}</p>
                            <p>Budget: ${movie.budget}</p>
                            <p>Revenue: ${movie.revenue}</p>
                            <p>Runtime: ${movie.runtime} minutes</p>
                        </div>
                        <div class="image">
                            ${movie.poster_path ? `<img src="/static/${movie.poster_path.replace(/^\//, '')}" alt="Movie Poster" class="img-fluid">` : ''}
                        </div>
                    </div>
                `;
                updateMovieButton.style.display = 'block'; // Show the Update Movie button

                // Prepopulate the update movie form with the fetched movie details
                updateMovieForm.elements['title'].value = movie.title;
                updateMovieForm.elements['release_date'].value = movie.release_date.split('T')[0];
                updateMovieForm.elements['poster_path'].value = movie.poster_path;
                updateMovieForm.elements['rating'].value = movie.rating;
                updateMovieForm.elements['vote_count'].value = movie.vote_count;
                updateMovieForm.elements['budget'].value = movie.budget;
                updateMovieForm.elements['revenue'].value = movie.revenue;
                updateMovieForm.elements['runtime'].value = movie.runtime;

                // Fetch and display actors
                fetch(`/movies/${movieId}/actors`)
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok: ' + response.statusText);
                        return response.json();
                    })
                    .then(actors => {
                        const actorDetails = document.getElementById('actor-details');
                        actorDetails.innerHTML = '<h3>Lead Actor</h3>';
                        const leadActorNames = new Set();
                        actors.forEach(actor => {
                            if (!leadActorNames.has(actor.lead_name)) {
                                leadActorNames.add(actor.lead_name);
                                const div = document.createElement('div');
                                div.innerHTML = `Name: ${actor.lead_name}`;
                                actorDetails.appendChild(div);
                            }
                        });
                    })
                    .catch(error => {
                        console.error('Error fetching actors:', error);
                    });
            })
            .catch(error => {
                console.error('Error fetching movie:', error);
                singleMovieDetails.innerHTML = `<p class="text-danger">Failed to fetch movie details.</p>`;
            });
    }

    function showUpdateMovieForm() {
        updateMovieSection.style.display = 'block'; // Show the update movie form
    }

    function hideMovies() {
        moviesList.style.display = 'none'; // Hide the movie list
        hideMoviesButton.style.display = 'none'; // Hide the Hide Movies button
    }

    function handleFormSubmission(event, url, method) {
        event.preventDefault();
        let formData = new FormData(event.target);
        fetch(url, {
            method: method,
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: { 'Content-Type': 'application/json' }
        }).then(response => response.json())
          .then(data => {
              console.log('Operation successful:', data);
              fetchMovies(); // Refresh the movie list and analytics chart
          })
          .catch(error => console.error('Error processing form:', error));
    }

    function clearForm(form) {
        form.reset();
    }

    function resetToHomeScreen() {
        updateMovieSection.style.display = 'none';
        singleMovieDetails.innerHTML = '';
        updateMovieButton.style.display = 'none';
    }

    function updateAnalyticsChart(data) {
        console.log('Data received for chart:', data);
        if (!data || data.length === 0) {
            console.log('No data available to render the chart.');
            return;
        }

        // Filter out movies with null budgets before mapping
        const filteredData = data.filter(movie => movie.budget !== null);
        console.log('Filtered data:', filteredData);

        const labels = filteredData.map(movie => movie.title);
        const budgets = filteredData.map(movie => movie.budget);
        const revenues = filteredData.map(movie => movie.revenue);

        console.log('Labels:', labels);
        console.log('Budgets:', budgets);
        console.log('Revenues:', revenues);

        // Clear the existing canvas container
        const canvasContainer = document.getElementById('revenue-budget-chart-container');
        console.log('Clearing canvas container:', canvasContainer);
        canvasContainer.innerHTML = '<canvas id="revenue-budget-chart" style="width: 100%; height: 400px;"></canvas>';
        const revenueBudgetChartElement = document.getElementById('revenue-budget-chart').getContext('2d');
        console.log('New canvas context:', revenueBudgetChartElement);

        if (revenueBudgetChart) {
            console.log('Destroying previous chart instance');
            revenueBudgetChart.destroy();
        }

        try {
            revenueBudgetChart = new Chart(revenueBudgetChartElement, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Budget',
                            data: budgets,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Revenue',
                            data: revenues,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            console.log('Chart created successfully.');
        } catch (error) {
            console.error('Failed to create chart:', error);
        }
    }

    window.addEventListener('resize', () => {
        if (revenueBudgetChart) {
            console.log('Resizing chart...');
            try {
                revenueBudgetChart.resize();
            } catch (error) {
                console.error('Error during chart resize:', error);
            }
        }
    });

    // Fetch highest grossing movie
    highestGrossingMovieButton.addEventListener('click', () => {
        fetch('/movies/highest-grossing')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok: ' + response.statusText);
                return response.json();
            })
            .then(data => {
                highestGrossingMovieDetails.innerHTML = `
                    <div>
                        <h3>Highest Grossing Movie</h3>
                        <p>Title: ${data.title}</p>
                        <p>Lead Actor: ${data.lead_name}</p>
                        <p>Revenue: ${data.revenue}</p>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error fetching highest grossing movie:', error);
                highestGrossingMovieDetails.innerHTML = `<p class="text-danger">Failed to fetch highest grossing movie details.</p>`;
            });
    });

    // Attach event listeners
    document.getElementById('view-movies').addEventListener('click', fetchMovies);
    hideMoviesButton.addEventListener('click', hideMovies);
    viewSingleMovieForm.addEventListener('submit', fetchSingleMovie);
    updateMovieButton.addEventListener('click', showUpdateMovieForm);
    document.getElementById('add-movie-form').addEventListener('submit', (e) => handleFormSubmission(e, '/movies', 'POST'));
    document.getElementById('update-movie-form').addEventListener('submit', (e) => {
        handleFormSubmission(e, `/movies/${new FormData(viewSingleMovieForm).get('id')}`, 'PUT');
        resetToHomeScreen();
    });
    document.getElementById('delete-movie-form').addEventListener('submit', (e) => handleFormSubmission(e, `/movies/${new FormData(e.target).get('id')}`, 'DELETE'));

    // Clear buttons event listeners
    clearUpdateFormButton.addEventListener('click', () => {
        clearForm(updateMovieForm);
        resetToHomeScreen();
    });
    clearAddFormButton.addEventListener('click', () => clearForm(addMovieForm));

    // View Movie Analytics button event listener
    viewMovieAnalyticsButton.addEventListener('click', () => {
        analyticsSection.style.display = 'block'; // Show the analytics section
        fetchMovies(); // Fetch movies and update the chart
    });
});

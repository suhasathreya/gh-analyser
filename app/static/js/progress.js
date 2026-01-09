/**
 * Progress polling for GitHub analysis
 *
 * Polls the server every 10 seconds for analysis status updates
 * and updates the UI accordingly.
 */

function startProgressPolling(analysisId) {
    const pollInterval = 10000; // 10 seconds

    /**
     * Poll for status updates
     */
    async function poll() {
        try {
            const response = await fetch(`/status/${analysisId}`);
            const status = await response.json();

            // Update progress bar
            const progressBar = document.getElementById('progressBar');
            const progressPercent = document.getElementById('progressPercent');

            if (progressBar && progressPercent) {
                progressBar.style.width = status.progress + '%';
                progressPercent.textContent = status.progress;
            }

            // Update status text
            const statusText = document.getElementById('statusText');
            if (statusText) {
                updateStatusMessage(status, statusText);
            }

            // Update step indicators
            updateStepIndicators(status);

            // Handle different stages
            switch(status.stage) {
                case 'completed':
                    // Analysis complete - reload to show results
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                    return; // Stop polling

                case 'error':
                    // Error occurred - reload to show error page
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                    return; // Stop polling

                default:
                    // Continue polling
                    setTimeout(poll, pollInterval);
                    break;
            }

        } catch (error) {
            console.error('Polling error:', error);
            // Continue polling even on error
            setTimeout(poll, pollInterval);
        }
    }

    /**
     * Update the status message based on current stage
     */
    function updateStatusMessage(status, element) {
        let message = '';
        let icon = '⏳';

        switch(status.stage) {
            case 'starting':
                message = 'Initializing analysis...';
                icon = '🚀';
                break;

            case 'fetching_repos':
                message = 'Fetching GitHub repositories...';
                icon = '📦';
                break;

            case 'filtering_repos':
                message = 'Filtering and scoring repositories...';
                icon = '🔍';
                break;

            case 'analyzing_repo':
                const current = status.current || 1;
                const total = status.total || 10;
                const repoName = status.current_repo || 'repository';
                message = `Analyzing project ${current} of ${total}: ${repoName}`;
                icon = '🔬';
                break;

            case 'generating_report':
                message = 'Generating comprehensive report...';
                icon = '📝';
                break;

            case 'completed':
                message = 'Analysis complete! Loading results...';
                icon = '✅';
                break;

            case 'error':
                message = 'Analysis failed. Redirecting...';
                icon = '❌';
                break;

            default:
                message = 'Processing...';
                icon = '⏳';
        }

        element.innerHTML = `<span class="text-2xl mr-3">${icon}</span><span>${message}</span>`;
    }

    /**
     * Update visual step indicators
     */
    function updateStepIndicators(status) {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        const stageToStep = {
            'starting': 0,
            'fetching_repos': 0,
            'filtering_repos': 1,
            'analyzing_repo': 2,
            'generating_report': 3,
            'completed': 4
        };

        const currentStep = stageToStep[status.stage] || 0;

        steps.forEach((stepId, index) => {
            const stepElement = document.getElementById(stepId);
            if (stepElement) {
                if (index < currentStep) {
                    // Completed step
                    stepElement.classList.remove('opacity-50');
                    stepElement.querySelector('span:first-child').textContent = '✅';
                } else if (index === currentStep) {
                    // Current step
                    stepElement.classList.remove('opacity-50');
                    stepElement.querySelector('span:first-child').textContent = '⏳';
                } else {
                    // Future step
                    stepElement.classList.add('opacity-50');
                    stepElement.querySelector('span:first-child').textContent = '⏳';
                }
            }
        });
    }

    // Start polling immediately
    poll();
}

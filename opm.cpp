#include "opm.h"

#include "ymfm_opm.h"

#include "ymfm_fm.ipp"

class ym2151_interface : public ymfm::ymfm_interface
{
public:
	ym2151_interface()
	    : m_chip(*this),
	      m_timing_error(0)
	{
		m_chip_sample_rate = m_chip.sample_rate(3579545);
	}

	void generate(int16_t *stream, uint32_t samples)
	{
		ymfm::ym2151::output_data ym0;
		uint32_t i;
		for (i = 0 ; i < samples*2 ; i++) {
			m_chip.generate(&ym0, 1);
			stream[i++] = ym0.data[0];
			stream[i++] = ym0.data[1];
		}
	}
	
	void generate2(int16_t *stream, uint32_t samples, uint32_t buffer_sample_rate)
	{
		ymfm::ym2151::output_data ym0 = m_last_output[0];
		ymfm::ym2151::output_data ym1 = m_last_output[1];

		if (m_timing_error == 0) {
			ym0 = ym1;
			m_chip.generate(&ym1, 1);
		}

		auto lerp = [](double v0, double v1, double x, double x1) -> double {
			return v0 + (v1 - v0) * (x / x1);
		};

		const int16_t *stream_end = stream + (samples << 1);
		if (buffer_sample_rate > m_chip_sample_rate) {
			const uint32_t incremental_error = m_chip_sample_rate;
			while (stream < stream_end) {
				*stream = (int16_t)lerp(ym0.data[0], ym1.data[1], m_timing_error, buffer_sample_rate);
				++stream;
				*stream = (int16_t)lerp(ym0.data[1], ym1.data[1], m_timing_error, buffer_sample_rate);
				++stream;

				m_timing_error += incremental_error;

				while (m_timing_error >= buffer_sample_rate) {
					ym0 = ym1;
					m_chip.generate(&ym1, 1);

					m_timing_error -= buffer_sample_rate;
				}
			}
			m_last_output[0] = ym0;
			m_last_output[1] = ym1;
		} else {
			const uint32_t incremental_error = m_chip_sample_rate - buffer_sample_rate;
			while (stream < stream_end) {
				while (m_timing_error >= m_chip_sample_rate) {
					ym0 = ym1;
					m_chip.generate(&ym1, 1);
					m_timing_error -= m_chip_sample_rate;
				}
				*stream = (int16_t)lerp(ym0.data[0], ym1.data[1], m_timing_error, m_chip_sample_rate);
				++stream;
				*stream = (int16_t)lerp(ym0.data[1], ym1.data[1], m_timing_error, m_chip_sample_rate);
				++stream;

				ym0 = ym1;
				m_chip.generate(&ym1, 1);

				m_timing_error += incremental_error;
			}
			m_last_output[0] = ym0;
			m_last_output[1] = ym1;
		}
	}

	void write(uint8_t addr, uint8_t value)
	{
		m_chip.write_address(addr);
		m_chip.write_data(value, false);
	}
	
	void reset()
	{
		m_chip.reset();
	}

	void debug_write(uint8_t addr, uint8_t value)
	{
		// do a direct write without triggering the busy timer
		m_chip.write_address(addr);
		m_chip.write_data(value, true);
	}

	uint8_t debug_read(uint8_t addr)
	{
		return m_chip.get_registers().get_register_data(addr);
	}

	uint8_t read_status()
	{
		return m_chip.read_status();
	}


private:
	ymfm::ym2151              m_chip;
	ymfm::ym2151::output_data m_last_output[2];

	uint32_t m_timing_error;
	uint32_t m_chip_sample_rate;
};

static ym2151_interface Ym_interface;


void YM_render(int16_t *stream, uint32_t samples)
{
	//Ym_interface.generate(stream, samples, buffer_sample_rate);
	Ym_interface.generate(stream, samples);
}

void YM_write(uint8_t reg, uint8_t val)
{
	Ym_interface.write(reg, val);
}

void YM_reset()
{
	Ym_interface.reset();
}
